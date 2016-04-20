from django.contrib.auth.models import User
from django.core.validators import validate_email

class EmailBackend(object):
    def authenticate(self, username=None, password=None):
        if validate_email.search(username):
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        if user.check_password(password):
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None