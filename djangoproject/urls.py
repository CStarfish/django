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
    path('about/', views.AboutView, name='about'),
    # Views for about page
    path('about/jly.html/', views.About1View, name='about1'),
    path('about/jwong.html/', views.About2View, name='about2'),
    path('about/erik.html/', views.About3View, name='about3'),
    path('about/bilgunn.html/', views.About4View, name='about4'),
    path('about/haolongd.html/', views.About5View, name='about5'),
    path('about/pablo.html/', views.About6View, name='about6'),
    path('about/madhura.html/', views.About7View, name='about7'),

    path('admin/', admin.site.urls),
    path('search/', views.SearchView.as_view(), name='search'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('password_reset/', views.ResetPasswordView.as_view(), name='password_reset'),
    
    #path('password_reset/', auth_views.PasswordResetView.as_view(template_name='djangoapp/password_reset.html'), 
        #name='password_reset'),
    #path('password_reset/done/', 
         #auth_views.PasswordResetDoneView.as_view(template_name='djangoapp/home.html'), 
         #name='password_reset_done'),
         
    path('password_reset_confirm/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='djangoapp/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('password_reset_complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='djangoapp/password_reset_complete.html'),
        name='password_reset_complete'),
    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/<int:user_id>', views.ProfileView.as_view(), name='profile'),
    path('candidacy/', views.CandidacyView.as_view(), name='candidacy'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/<int:user_id>', views.ProfileView.as_view(), name='profile'),
    path('profile_page/<int:user_id>', views.ProfilePageView.as_view(), name='profile_page'),
    path('policy_creation/', views.PolicyCreationView.as_view(), name='policy_creation'),
    path('policy_page/<int:policy_id>', views.PolicyPageView, name='policy_page'),
    path('event_creation/', views.EventCreationView.as_view(), name='event_creation'),
    path('event_page/<int:event_id>', views.EventPageView, name='event_page'),
    path('election_office/<int:user_id>', views.ElectionOfficeView, name='election_office'),
    path('polling_creation/', views.PollingCreationView.as_view(), name='polling_creation'),
    path('polling_location/<int:polling_location_id>', views.PollingLocationView, name='polling_location')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
