from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    app_name = 'home'
    template_name = f'{app_name}/index.html'
    
