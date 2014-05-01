from jose.configurations import Configuration as BaseConf
from connect.confs import Store


class JoseConf(BaseConf):
    def __init__(self, store=None, *args, **kwargs):
        self.store = Store(self)
