from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('<int:movie_id>/', movie),
    path('movie_review/add/<int:movie_id>/', add_review),
    path('movie_reviews/<int:movie_id>/', movie_reviews, name='movie_reviews'),
    path('', index), 
    path('<int:movie_id>/', views.movie, name='movie'),
    path('<int:movie_id>/like/', views.toggle_like, name='toggle_like'),
    path('favorites/', views.favorites, name='favorites'),
    path("actors/<int:actor_id>/", views.actor_detail, name="actor_detail"),
    path("movie_review/add/<int:movie_id>/", views.add_review, name="add_review"),
    path("movie_review/delete/<int:review_id>/", views.delete_review, name="delete_review"),
    path("movies/search/", views.search_movies, name="search_movies"),

] 
