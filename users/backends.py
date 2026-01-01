from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


user_model = get_user_model()

class MobileBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        mobile = username 
        
        if mobile is None or password is None:
            return None
        try:
            user = user_model.objects.get(mobile=mobile)
        except user_model.DoesNotExist:
            return None
        
        if user.check_password(password) and user.is_active:
            return user
        
        return None
    