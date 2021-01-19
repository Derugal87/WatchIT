from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='film-home'),
    path('show/', views.show, name='films'),
    path('show/<int:showid>/', views.show, name='films'),
    path('profile/', views.profile, name='filmslist'),
    path('profile/<str:username>/', views.profile, name='filmslist'),
    path('search/', views.search, name='filmsearch'),
    path('search/<str:query>/', views.search, name='filmsearch')
]