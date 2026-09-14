from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, ReviewReport
from .forms import ReviewReportForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden, Http404
from django.views.decorators.http import require_http_methods

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, is_hidden=False)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, movie_id=id, is_hidden=False)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, movie_id=id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)


@login_required
@require_http_methods(['GET', 'POST'])
def report_review(request, id, review_id):
    with transaction.atomic():
        review = get_object_or_404(Review.objects.select_for_update(), id=review_id, movie_id=id)
        if review.user_id == request.user.id:
            return HttpResponseForbidden('You can delete your own review instead of reporting it.')
        if ReviewReport.objects.filter(review=review, reporter=request.user).exists():
            messages.info(request, 'You have already reported this review. Your report is saved.')
            return redirect('movies.show', id=id)
        if review.is_hidden:
            raise Http404('This review is no longer available.')
        form = ReviewReportForm(request.POST if request.method == 'POST' else None)
        if request.method == 'POST' and form.is_valid():
            report = form.save(commit=False)
            report.review = review
            report.reporter = request.user
            report.save()
            review.is_hidden = True
            review.save(update_fields=['is_hidden'])
            messages.success(request, 'Report submitted. The review has been hidden from the movie page pending staff review.')
            return redirect('movies.show', id=id)
    return render(request, 'movies/report_review.html', {
        'template_data': {'title': 'Report review'}, 'review': review, 'form': form,
    })
