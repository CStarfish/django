"""
URL configuration for djangoproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from djangoapp import views
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(url='home/', permanent=True)),
    path('home/', views.HomeView, name='home'),
    path('admin/', admin.site.urls),
    path('search/', views.SearchView.as_view(), name='search'),
    path('results/', views.ResultsView, name='results'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='djangoapp/password_reset.html'), 
        name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='djangoapp/home.html'), 
         name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='djangoapp/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('password_reset_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='djangoapp/password_reset_complete.html'),
        name='password_reset_complete'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/<int:user_id>', views.ProfileView.as_view(), name='profile'),
    path('candidacy/', views.CandidacyView.as_view(), name='candidacy')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
