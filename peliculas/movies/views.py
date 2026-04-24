from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from movies.models import Movie, MovieReview, MovieLike
from movies.forms import MovieReviewForm
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings

# Create your views here.
def index(request):
    movies = Movie.objects.all()
    context = { 'movies':movies, 'message':'welcome' }
    return render(request,'movies/index.html', context=context )
    
def movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = MovieLike.objects.filter(user=request.user, movie=movie).exists()

    # Llamada a la API de TMDb para obtener reparto
    cast = []
    if movie.tmdb_id:
        url = f"https://api.themoviedb.org/3/movie/{movie.tmdb_id}/credits?api_key={settings.TMDB_API_KEY}&language=es"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            cast = data.get("cast", [])

    return render(request, "movies/movie.html", {
        "movie": movie,
        "user_has_liked": user_has_liked,
        "cast": cast,
    })

def movie_reviews(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    return render(request,'movies/reviews.html', context={'movie':movie } )
    
def add_review(request, movie_id):
    form = None
    movie = Movie.objects.get(id=movie_id)
    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            title  = form.cleaned_data['title']
            review = form.cleaned_data['review']
            movie_review = MovieReview(
                    movie=movie,
                    rating=rating,
                    title=title,
                    review=review,
                    user=request.user)
            movie_review.save()
            return HttpResponse(status=204,
                                headers={'HX-Trigger': 'listChanged'})
    else:
        form = MovieReviewForm()
        return render(request,
                  'movies/movie_review_form.html',
                  {'movie_review_form': form, 'movie':movie})
@login_required
def toggle_like(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    like, created = MovieLike.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        like.delete()
    return redirect("movie", movie_id=movie.id)   
@login_required
def favorites(request):
    # obtenemos todas las películas que el usuario ha dado like
    liked_movies = Movie.objects.filter(likes__user=request.user)
    return render(request, "movies/favorites.html", {"movies": liked_movies})
