from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views as V

app_name = 'users'

urlpatterns = [
    path('login/', V.UserLoginView.as_view(), name='login'),
    path('register/', V.UserRegisterView.as_view(), name='register'),
    path("logout/", V.UserLogoutView.as_view(), name="logout"),
]
