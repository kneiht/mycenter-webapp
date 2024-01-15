from django.urls import re_path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    # AUTHENTICATION
    re_path(r'^account/login/?$', views.UserLoginView.as_view(), name='login'),
    re_path(r'^account/logout/?$', views.logout_view, name='logout'),
    re_path(r'^account/register/?$', views.register, name='register'),
    re_path(r'^account/password-change/?$', views.UserPasswordChangeView.as_view(), name='password_change'),
    re_path(r'^account/password-change-done/?$', views.password_change_done, name="password_change_done"),
    
    re_path(r'^account/password-reset/?$', views.UserPasswordResetView.as_view(), name='password_reset'),
    re_path(r'^account/password-reset-confirm/(?P<uidb64>[\w-]+)/(?P<token>[\w-]+)/?$',views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^account/password-reset-done/?$', views.UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^account/password-reset-complete/?$', views.UserPasswordResetCompleteView.as_view()   , name='password_reset_complete'),
]


