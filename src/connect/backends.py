from django.contrib.auth.models import User

class AuthUserBackend(object):
    def authenticate(self, user):
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
