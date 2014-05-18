from connect.api.auth import ConnectAuth
from connect.az.models import Token
import re
import traceback

_re = re.compile(r'Bearer\s+(?P<token>\S+)$')

class BearerTokenAuth(ConnectAuth):
    """ OAuth Bearer Token
    """
    def __init__(self, **kwargs):
        super(BearerTokenAuth, self).__init__(**kwargs)

    def is_authenticated(self, request, **kwargs):
        print "authentication bearer...", self.context
        try:
            auth = request.META.get('HTTP_AUTHORIZATION', None)
            if auth is None:
                #: TODO: fine error handling
                return False
            token = _re.search(auth)
            self.token = token and Token.objects.get(
                token=token.groupdict()['token'],
                signon__authority__tenant=self.context['tenant'])

            if self.token is None:
                #: TODO: fine error handling
                return False

            for scope in self.scopes:
                if not self.token.scopes.filter(scope=scope).exists():
                    #: TODO: fine error handling
                    return False

        except:
            #: TODO: fine error handling
            print traceback.format_exc()
            return False 

        return True

    def get_identifier(self, request):
        """
        """
        return self.token and self.token.signon and self.token.signon.subject


