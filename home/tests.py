from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from movies.models import Movie, Review
from cart.models import Order, Item


class TutorialWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('reviewer', password='test-only-password')
        cls.other = User.objects.create_user('other', password='test-only-password')
        cls.movie = Movie.objects.create(name='Inception', price=12, description='A heist.', image='movie_images/inception.jpg')
        cls.second = Movie.objects.create(name='Avatar', price=13, description='Another world.', image='movie_images/avatar.jpg')

    def test_public_pages_and_search(self):
        for name in ['home.index', 'home.about', 'movies.index', 'accounts.signup', 'accounts.login', 'cart.index']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)
        response = self.client.get(reverse('movies.index'), {'search': 'INCEP'})
        self.assertContains(response, 'Inception')
        self.assertNotContains(response, 'Avatar')
        self.assertEqual(self.client.get(reverse('movies.show', args=[self.movie.id])).status_code, 200)

    def test_signup_login_logout(self):
        response = self.client.post(reverse('accounts.signup'), {'username': 'newviewer', 'password1': 'Movie-demo-927!x', 'password2': 'Movie-demo-927!x'})
        self.assertRedirects(response, reverse('accounts.login'))
        self.assertTrue(User.objects.filter(username='newviewer').exists())
        self.assertContains(self.client.post(reverse('accounts.login'), {'username': 'newviewer', 'password': 'wrong'}), 'incorrect')
        self.assertRedirects(self.client.post(reverse('accounts.login'), {'username': 'newviewer', 'password': 'Movie-demo-927!x'}), reverse('home.index'))
        self.assertRedirects(self.client.get(reverse('accounts.logout')), reverse('home.index'))

    def test_protected_pages_redirect_to_login(self):
        for name in ['accounts.orders', 'cart.purchase']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.url.startswith(reverse('accounts.login')))

    def test_review_create_edit_delete_and_ownership(self):
        self.client.force_login(self.user)
        self.client.post(reverse('movies.create_review', args=[self.movie.id]), {'comment': 'Excellent movie.'})
        review = Review.objects.get(user=self.user)
        edit = reverse('movies.edit_review', args=[self.movie.id, review.id])
        delete = reverse('movies.delete_review', args=[self.movie.id, review.id])
        self.assertEqual(self.client.get(edit).status_code, 200)
        self.client.post(edit, {'comment': 'A thoughtful thriller.'})
        review.refresh_from_db()
        self.assertEqual(review.comment, 'A thoughtful thriller.')
        self.client.force_login(self.other)
        self.client.post(edit, {'comment': 'Unauthorized edit'})
        review.refresh_from_db()
        self.assertEqual(review.comment, 'A thoughtful thriller.')
        self.assertEqual(self.client.get(delete).status_code, 404)
        self.client.force_login(self.user)
        self.client.get(delete)
        self.assertFalse(Review.objects.filter(pk=review.pk).exists())

    def test_cart_purchase_and_private_order_history(self):
        self.client.force_login(self.user)
        self.client.post(reverse('cart.add', args=[self.movie.id]), {'quantity': 2})
        self.client.post(reverse('cart.add', args=[self.second.id]), {'quantity': 1})
        response = self.client.get(reverse('cart.index'))
        self.assertEqual(response.context['template_data']['cart_total'], 37)
        self.assertEqual(self.client.get(reverse('cart.purchase')).status_code, 200)
        order = Order.objects.get(user=self.user)
        self.assertEqual(order.total, 37)
        self.assertEqual(Item.objects.filter(order=order).count(), 2)
        self.assertEqual(self.client.session['cart'], {})
        response = self.client.get(reverse('accounts.orders'))
        self.assertEqual(list(response.context['template_data']['orders']), [order])
        self.client.force_login(self.other)
        response = self.client.get(reverse('accounts.orders'))
        self.assertEqual(list(response.context['template_data']['orders']), [])

    def test_clear_and_empty_checkout(self):
        self.client.force_login(self.user)
        self.client.post(reverse('cart.add', args=[self.movie.id]), {'quantity': 1})
        self.client.get(reverse('cart.clear'))
        self.assertEqual(self.client.session['cart'], {})
        self.assertRedirects(self.client.get(reverse('cart.purchase')), reverse('cart.index'))
        self.assertEqual(Order.objects.count(), 0)

    def test_admin_access(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get('/admin/').status_code, 302)
        self.user.is_staff = self.user.is_superuser = True
        self.user.save()
        for path in ['/admin/', '/admin/movies/movie/', '/admin/movies/review/', '/admin/cart/order/', '/admin/cart/item/']:
            self.assertEqual(self.client.get(path).status_code, 200)
