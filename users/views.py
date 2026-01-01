from django.contrib.auth.views import LoginView
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import redirect
from django.views import View

from .forms import LoginForm, RegisterForm
from .models import User
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST

# User = get_user_model()

class UserLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home:main')

    def form_invalid(self, form):
        
        messages.error(
            self.request,
            'شماره موبایل یا رمز عبور اشتباه است'
        )
        return super().form_invalid(form)
    
class UserRegisterView(FormView):
    template_name = 'users/register.html'
    form_class = RegisterForm
    
    
    def form_valid(self, form):
        user = User.objects.create_user(
            mobile=form.cleaned_data['mobile'],
            password=form.cleaned_data['password1'],
            is_active=True 
        )
        
        login(self.request, user)
        return redirect('/', messages.success(request=self.request, message="با موفقیت وارد شدید"))


class UserLogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            print(user)
            logout(request,)
            return redirect('/', messages.success(request, message="با موفقیت خارج شدید"))
        else:
            return redirect('users:login')