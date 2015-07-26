from tastypie.authentication import Authentication 


class ConnectAuth(Authentication):
    def __init__(
            self, 
            scopes=[], 
            resource=None, 
            *args, **kwargs):

        super(ConnectAuth, self).__init__(*args, **kwargs)

        self.scopes = scopes        #: required scopes

        self.party = None       #: requesting RelyingParty
        self.signon = None      #: granting SignOn

        self.resource = resource    #: protected Resource Object(RESERVED...)
        self.protection = None      #: remote protection(RESERVE for UMA or ...)
        self.context = None         #: requesting context
