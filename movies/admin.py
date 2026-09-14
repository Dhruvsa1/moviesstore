from django.contrib import admin
from .models import Movie, Review, ReviewReport
from django.db import transaction

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

admin.site.register(Movie, MovieAdmin)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'movie', 'user', 'date', 'is_hidden']
    list_filter = ['is_hidden']
    search_fields = ['comment', 'movie__name', 'user__username']
    readonly_fields = ['is_hidden']


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'reporter', 'reason', 'status', 'created_at']
    list_filter = ['status', 'reason']
    search_fields = ['review__comment', 'review__movie__name', 'reporter__username', 'details']
    readonly_fields = ['review', 'reporter', 'reason', 'details', 'created_at', 'status']
    actions = ['uphold_reports', 'dismiss_reports']

    def has_add_permission(self, request):
        return False

    def has_moderate_permission(self, request):
        return request.user.has_perm('movies.change_review') and request.user.has_perm('movies.change_reviewreport')

    @admin.action(description='Uphold reports and keep reviews hidden', permissions=['moderate'])
    def uphold_reports(self, request, queryset):
        self._moderate(request, queryset, True, ReviewReport.Status.UPHELD)

    @admin.action(description='Dismiss reports and restore reviews', permissions=['moderate'])
    def dismiss_reports(self, request, queryset):
        self._moderate(request, queryset, False, ReviewReport.Status.DISMISSED)

    def _moderate(self, request, queryset, hidden, status):
        with transaction.atomic():
            review_ids = list(queryset.values_list('review_id', flat=True).distinct())
            reviews = list(Review.objects.select_for_update().filter(pk__in=review_ids))
            Review.objects.filter(pk__in=review_ids).update(is_hidden=hidden)
            ReviewReport.objects.filter(review_id__in=review_ids).update(status=status)
            for review in reviews:
                self.log_change(request, review, f'Review reports {status}; hidden={hidden}.')
        self.message_user(request, f'{len(review_ids)} review(s) moderated.')
