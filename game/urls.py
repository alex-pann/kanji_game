from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='game/login.html'), name='login'),
    path('game/', views.game_view, name='game'),
    path('ranking/', views.ranking, name='ranking'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('nopage/', views.nopage, name='nopage'),
    path('dictionary/', views.dictionary, name='dictionary'),
]