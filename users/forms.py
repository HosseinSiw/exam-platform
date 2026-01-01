from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()

class LoginForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        self.fields['username'].label = 'شماره موبایل'
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '09xxxxxxxxx'
        })
        self.fields['password'].label = "رمز ورود"
        self.fields['password'].widget.attrs.update({
            'class': 'form-control'
        })


class RegisterForm(forms.Form):
    mobile = forms.CharField(
        max_length=11,
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09xxxxxxxxx'
        }))
    
    password1 = forms.CharField(
        label='رمز عبور ',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean_mobile(self):
        mobile = self.cleaned_data['mobile']
        if User.objects.filter(mobile=mobile).exists():
            raise ValidationError("این شماره موبایل قبلا استفاده شده است")
        
        return mobile 
       
    def clean(self):
        clean_data = super().clean()
        
        p1, p2 = clean_data.get('password1'), clean_data.get('password2')
        
        if p1 and p2 and p1 != p2:
            raise ValidationError('رمز عبور و تکرار آن یکسان نیستند')
        
        return clean_data

        