from jose.base import BaseObject


class Link(BaseObject):
    _fields = dict(
        rel=None,
        type=None,
        href=None,
        titles={},
        properties={},
    )


class Jrd(BaseObject):
    _fields = dict(
        subject='',
        aliases=[],     # list(str)
        links=[],       # list(Link)
    )
    _media_type = 'application/jrd+json'

    def __init__(self, *args, **kwargs):
        super(Jrd, self).__init__(*args, **kwargs)
        if isinstance(self.links, list):
            new_links = []
            for link in self.links:
                if isinstance(link, Link):
                    new_links.append(link)
                if isinstance(link, dict):
                    new_links.append(Link(**link))
            self.links = new_links
