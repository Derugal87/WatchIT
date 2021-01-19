from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
import film.views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name="film/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="film/logout.html"), name='logout'),
    path('profile/', user_views.profile, name='profile'),
    path('profile/<str:username>/', user_views.profile, name='profile'),
    path('', include('film.urls')),
]
