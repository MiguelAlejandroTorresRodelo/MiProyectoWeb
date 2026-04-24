from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from movies.models import Movie, MovieReview, MovieLike
from movies.forms import MovieReviewForm
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings
from django.contrib import messages


# Create your views here.
def index(request):
    movies = Movie.objects.all()
    context = { 'movies':movies, 'message':'welcome' }
    return render(request,'movies/index.html', context=context )

def search_movies(request):
    query = request.GET.get("search", "")
    movies = Movie.objects.filter(title__icontains=query) if query else []
    return render(request, "movies/search_results.html", {"movies": movies, "query": query})

    
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
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            movie_review = form.save(commit=False)
            movie_review.movie = movie
            movie_review.user = request.user
            movie_review.save()
            return redirect("movie", movie_id=movie_id)
    else:
        form = MovieReviewForm()

    return render(request, "movies/movie_review_form.html", {
        "movie_review_form": form,
        "movie": movie
    })



def actor_detail(request, actor_id):
    # Datos del actor
    url_actor = f"https://api.themoviedb.org/3/person/{actor_id}?api_key={settings.TMDB_API_KEY}&language=es"
    actor_data = requests.get(url_actor).json()

    # Películas en las que ha participado
    url_credits = f"https://api.themoviedb.org/3/person/{actor_id}/movie_credits?api_key={settings.TMDB_API_KEY}&language=es"
    credits_data = requests.get(url_credits).json()
    movies = credits_data.get("cast", [])

    return render(request, "movies/actor.html", {
        "actor": actor_data,
        "movies": movies,
    })
def delete_review(request, review_id):
    review = get_object_or_404(MovieReview, id=review_id)

    if review.user != request.user:
        messages.error(request, "No puedes eliminar reseñas de otros usuarios.")
        return redirect("movie", movie_id=review.movie.id) 

    review.delete()
    messages.success(request, "Reseña eliminada correctamente.")
    return redirect("movie", movie_id=review.movie.id)  


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
