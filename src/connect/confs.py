from jose.store import FileStore


class Store(FileStore):

    def save(self, obj, owner, id=None, *args, **kwargs):
        owner.save_object(obj, id, *args, **kwargs)

    def load(self, obj_class, owner, id=None, *args, **kwargs):
        return owner.load_object(obj_class, id, *args, **kwargs)
