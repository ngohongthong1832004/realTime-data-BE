from django.urls import path
from .views import *


urlpatterns = [
    # user
    path('register/', Register.as_view(), name='user-registration'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

    # ok
    path('weather/', WeatherAPI.as_view(), name='weather'),
    path("quotes/", QuotesAPI.as_view(), name="quotes"),
    path("foods/", FoodAPI.as_view(), name="food"),
    path("musics/", MusicAPI.as_view(), name="music"),
    path("news/", NewsAPI.as_view(), name="news"),
    path("books/", BooksAPI.as_view(), name="books"),
    path("movies/", MoviesAPI.as_view(), name="movies"),


    # bad



    path('', Home.as_view(), name='home'),
    path("craw/", ScrapeDataView.as_view(), name="craw")
]
    