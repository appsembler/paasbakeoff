from django.core.files.base import File

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO



class GSBotoStorageFile(File):
    def __init__(self, name, mode, storage):
        self._storage = storage
        self.name = name[len(self._storage.location):].lstrip('/')
        self._mode = mode
        self.key = storage.bucket.get_key(self._storage._encode_name(name))
        self._is_dirty = False
        self._file = None

    @property
    def size(self):
        return self.key.size

    @property
    def file(self):
        if self._file is None:
            self._file = StringIO()
            if 'r' in self._mode:
                self._is_dirty = False
                self.key.get_contents_to_file(self._file)
                self._file.seek(0)
        return self._file

    def read(self, *args, **kwargs):
        if 'r' not in self._mode:
            raise AttributeError("File was not opened in read mode.")
        return super(GSBotoStorageFile, self).read(*args, **kwargs)

    def write(self, *args, **kwargs):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self._is_dirty = True
        return super(GSBotoStorageFile, self).write(*args, **kwargs)

    def close(self):
        if self._is_dirty:
            self.key.set_contents_from_file(self._file, headers=self._storage.headers, policy=self._storage.acl)
        self.key.close()