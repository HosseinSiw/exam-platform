from django.urls import path
from . import views as V


app_name = 'home'

urlpatterns = [
    path('', V.HomeView.as_view(), name='home'),
]