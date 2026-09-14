from django.contrib.auth.models import Permission, User
from django.test import Client, TestCase
from django.urls import reverse
from .models import Movie, Review, ReviewReport


class ReviewReportingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user('author', password='test-only-password')
        cls.reporter = User.objects.create_user('reporter', password='test-only-password')
        cls.movie = Movie.objects.create(name='Example', price=12, description='Demo', image='movie_images/inception.jpg')
        cls.other_movie = Movie.objects.create(name='Other', price=10, description='Demo', image='movie_images/avatar.jpg')

    def setUp(self):
        self.review = Review.objects.create(movie=self.movie, user=self.author, comment='A review to moderate.')
        self.url = reverse('movies.report_review', args=[self.movie.pk, self.review.pk])
        self.detail = reverse('movies.show', args=[self.movie.pk])
        self.client.force_login(self.reporter)

    def report(self):
        return self.client.post(self.url, {'reason': 'spam', 'details': 'Irrelevant promotional content.'})

    def test_submission_hides_review_for_everyone_and_persists_report(self):
        self.assertContains(self.client.get(self.detail), 'Report review')
        self.assertRedirects(self.report(), self.detail)
        report = ReviewReport.objects.get(review=self.review)
        self.assertEqual(report.reporter, self.reporter)
        self.assertEqual(report.reason, 'spam')
        self.assertEqual(report.details, 'Irrelevant promotional content.')
        self.assertEqual(report.status, ReviewReport.Status.PENDING)
        self.review.refresh_from_db()
        self.assertTrue(self.review.is_hidden)
        for viewer in [None, self.reporter, self.author]:
            self.client.logout()
            if viewer:
                self.client.force_login(viewer)
            self.assertNotContains(self.client.get(self.detail), self.review.comment)

    def test_get_and_invalid_form_do_not_hide_or_create_report(self):
        self.assertContains(self.client.get(self.url), 'Submit report')
        for data in [{}, {'reason': 'invalid'}, {'reason': 'spam', 'details': 'x' * 501}]:
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context['form'].errors)
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_hidden)
        self.assertFalse(ReviewReport.objects.exists())

    def test_authentication_and_csrf_are_required(self):
        self.client.logout()
        self.assertRedirects(self.report(), reverse('accounts.login') + '?next=' + self.url)
        protected = Client(enforce_csrf_checks=True)
        protected.force_login(self.reporter)
        self.assertEqual(protected.post(self.url, {'reason': 'spam'}).status_code, 403)
        self.assertFalse(ReviewReport.objects.exists())

    def test_own_review_and_mismatched_movie_cannot_be_reported(self):
        self.client.force_login(self.author)
        self.assertEqual(self.report().status_code, 403)
        self.assertNotContains(self.client.get(self.detail), 'Report review')
        self.client.force_login(self.reporter)
        mismatch = reverse('movies.report_review', args=[self.other_movie.pk, self.review.pk])
        self.assertEqual(self.client.post(mismatch, {'reason': 'spam'}).status_code, 404)
        self.assertFalse(ReviewReport.objects.exists())

    def test_duplicate_report_is_idempotent(self):
        self.report()
        self.assertRedirects(self.report(), self.detail)
        self.assertEqual(ReviewReport.objects.count(), 1)

    def test_reported_review_cannot_be_edited_or_reported_by_another_user(self):
        self.report()
        self.client.force_login(self.author)
        self.assertEqual(self.client.post(reverse('movies.edit_review', args=[self.movie.pk, self.review.pk]), {'comment': 'Replacement'}).status_code, 404)
        other = User.objects.create_user('another-reporter')
        self.client.force_login(other)
        self.assertEqual(self.report().status_code, 404)
        self.assertEqual(ReviewReport.objects.count(), 1)

    def test_staff_can_uphold_and_dismiss_reports(self):
        self.report()
        report = ReviewReport.objects.get()
        staff = User.objects.create_superuser('moderator', password='test-only-password')
        self.client.force_login(staff)
        url = reverse('admin:movies_reviewreport_changelist')
        for action, status, hidden in [('uphold_reports', ReviewReport.Status.UPHELD, True), ('dismiss_reports', ReviewReport.Status.DISMISSED, False)]:
            self.assertEqual(self.client.post(url, {'action': action, '_selected_action': report.pk}).status_code, 302)
            report.refresh_from_db()
            self.review.refresh_from_db()
            self.assertEqual(report.status, status)
            self.assertEqual(self.review.is_hidden, hidden)
        self.assertContains(self.client.get(self.detail), self.review.comment)
        self.client.force_login(self.reporter)
        self.report()
        self.review.refresh_from_db()
        self.assertFalse(self.review.is_hidden, 'A dismissed duplicate must not hide the restored review again')

    def test_moderation_requires_review_and_report_permissions(self):
        self.report()
        report = ReviewReport.objects.get()
        staff = User.objects.create_user('limited-staff', is_staff=True)
        staff.user_permissions.add(Permission.objects.get(codename='change_reviewreport'))
        self.client.force_login(staff)
        self.client.post(reverse('admin:movies_reviewreport_changelist'), {'action': 'dismiss_reports', '_selected_action': report.pk})
        self.review.refresh_from_db()
        self.assertTrue(self.review.is_hidden)
