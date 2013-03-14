import os

import mimetypes

from django.conf import settings
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.utils.encoding import force_unicode, smart_str

from .format import SubdomainCallingFormat
from .file import GSBotoStorageFile
from .utils import safe_join

try:
    from boto.gs.connection import GSConnection
    from boto.gs.key import Key
except ImportError:
    raise ImproperlyConfigured("Could not load Google Storage bindings.\n"
                               "See http://code.google.com/p/boto/")


ACCESS_KEY_NAME     = getattr(settings, 'GS_ACCESS_KEY_ID', None)
SECRET_KEY_NAME     = getattr(settings, 'GS_SECRET_ACCESS_KEY', None)
HEADERS             = getattr(settings, 'GS_HEADERS', {})
STORAGE_BUCKET_NAME = getattr(settings, 'GS_STORAGE_BUCKET_NAME', None)
AUTO_CREATE_BUCKET  = getattr(settings, 'GS_AUTO_CREATE_BUCKET', False)
DEFAULT_ACL         = getattr(settings, 'GS_DEFAULT_ACL', 'public-read')
BUCKET_ACL          = getattr(settings, 'GS_BUCKET_ACL', DEFAULT_ACL)
QUERYSTRING_AUTH    = getattr(settings, 'GS_QUERYSTRING_AUTH', True)
QUERYSTRING_EXPIRE  = getattr(settings, 'GS_QUERYSTRING_EXPIRE', 3600)
REDUCED_REDUNDANCY  = getattr(settings, 'GS_REDUCED_REDUNDANCY', False)
LOCATION            = getattr(settings, 'GS_LOCATION', '')
CUSTOM_DOMAIN       = getattr(settings, 'GS_CUSTOM_DOMAIN', None)
CALLING_FORMAT      = getattr(settings, 'GS_CALLING_FORMAT', SubdomainCallingFormat())
SECURE_URLS         = getattr(settings, 'GS_SECURE_URLS', True)
FILE_NAME_CHARSET   = getattr(settings, 'GS_FILE_NAME_CHARSET', 'utf-8')
FILE_OVERWRITE      = getattr(settings, 'GS_FILE_OVERWRITE', True)
IS_GZIPPED          = getattr(settings, 'GS_IS_GZIPPED', False)
PRELOAD_METADATA    = getattr(settings, 'GS_PRELOAD_METADATA', False)
GZIP_CONTENT_TYPES  = getattr(settings, 'GZIP_CONTENT_TYPES', (
    'text/css',
    'application/javascript',
    'application/x-javascript'
))


class GoogleStorage(Storage):
    def __init__(self, bucket=STORAGE_BUCKET_NAME, access_key=None,
                       secret_key=None, bucket_acl=BUCKET_ACL, acl=DEFAULT_ACL, headers=HEADERS,
                       gzip=IS_GZIPPED, gzip_content_types=GZIP_CONTENT_TYPES,
                       querystring_auth=QUERYSTRING_AUTH, querystring_expire=QUERYSTRING_EXPIRE,
                       reduced_redundancy=REDUCED_REDUNDANCY,
                       custom_domain=CUSTOM_DOMAIN, secure_urls=SECURE_URLS,
                       location=LOCATION, file_name_charset=FILE_NAME_CHARSET,
                       preload_metadata=PRELOAD_METADATA, calling_format=CALLING_FORMAT):

        self.bucket_acl = bucket_acl
        self.bucket_name = bucket
        self.acl = acl
        self.headers = headers
        self.preload_metadata = preload_metadata
        self.gzip = gzip
        self.gzip_content_types = gzip_content_types
        self.querystring_auth = querystring_auth
        self.querystring_expire = querystring_expire
        self.reduced_redundancy = reduced_redundancy
        self.custom_domain = custom_domain
        self.secure_urls = secure_urls
        self.location = location or ''
        self.location = self.location.lstrip('/')
        self.file_name_charset = file_name_charset

        if not access_key and not secret_key:
            print u'where are no secret keys.'
            access_key, secret_key = self._get_access_keys()

        self.connection = GSConnection(access_key, secret_key)
        
        self._entries = {}

    @property
    def bucket(self):
        if not hasattr(self, '_bucket'):
            self._bucket = self._get_or_create_bucket(self.bucket_name)
        return self._bucket

    @property
    def entries(self):
        if self.preload_metadata and not self._entries:
            self._entries = dict((self._decode_name(entry.key), entry)
                                for entry in self.bucket.list())
        return self._entries

    def _get_access_keys(self):
        access_key = ACCESS_KEY_NAME
        secret_key = SECRET_KEY_NAME
        if (access_key or secret_key) and (not access_key or not secret_key):
            access_key = os.environ.get(ACCESS_KEY_NAME)
            secret_key = os.environ.get(SECRET_KEY_NAME)

        if access_key and secret_key:
            # Both were provided, so use them
            return access_key, secret_key

        return None, None

    def _get_or_create_bucket(self, name):
        """Retrieves a bucket if it exists, otherwise creates it."""
        try:
            return self.connection.get_bucket(name, validate=AUTO_CREATE_BUCKET)
        except Exception, e:
            if AUTO_CREATE_BUCKET:
                bucket = self.connection.create_bucket(name)
                bucket.set_acl(self.bucket_acl)
                return bucket
            raise ImproperlyConfigured("%s" % str(e))

    def _clean_name(self, name):
        # Useful for windows' paths
        return os.path.normpath(name).replace('\\', '/')

    def _normalize_name(self, name):
        try:
            return safe_join(self.location, name).lstrip('/')
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." % name)

    def _encode_name(self, name):
        return smart_str(name, encoding=self.file_name_charset)

    def _decode_name(self, name):
        return force_unicode(name, encoding=self.file_name_charset)

    def _open(self, name, mode='rb'):
        name = self._normalize_name(self._clean_name(name))
        f = GSBotoStorageFile(name, mode, self)
        if not f.key:
            raise IOError('File does not exist: %s' % name)
        return f

    def _save(self, name, content):
        cleaned_name = self._clean_name(name)
        name = self._normalize_name(cleaned_name)
        headers = self.headers.copy()
        content_type = getattr(content, 'content_type', mimetypes.guess_type(name)[0] or Key.DefaultContentType)

        content.name = cleaned_name
        k = self.bucket.get_key(self._encode_name(name))
        if not k:
            k = self.bucket.new_key(self._encode_name(name))

        k.set_metadata('Content-Type', content_type)
        k.set_contents_from_file(content, headers=headers, policy=self.acl)
                                 #reduced_redundancy=self.reduced_redundancy)
        return cleaned_name

    def delete(self, name):
        name = self._normalize_name(self._clean_name(name))
        self.bucket.delete_key(self._encode_name(name))

    def exists(self, name):
        name = self._normalize_name(self._clean_name(name))
        if self.entries:
            return name in self.entries
        k = self.bucket.new_key(self._encode_name(name))
        return k.exists()

    def listdir(self, name):
        name = self._normalize_name(self._clean_name(name))
        dirlist = self.bucket.list(self._encode_name(name))
        files = []
        dirs = set()
        base_parts = name.split("/") if name else []
        for item in dirlist:
            parts = item.name.split("/")
            parts = parts[len(base_parts):]
            if len(parts) == 1:
                # File
                files.append(parts[0])
            elif len(parts) > 1:
                # Directory
                dirs.add(parts[0])
        return list(dirs), files

    def size(self, name):
        name = self._normalize_name(self._clean_name(name))
        if self.entries:
            entry = self.entries.get(name)
            if entry:
                return entry.size
            return 0
        return self.bucket.get_key(self._encode_name(name)).size

    def modified_time(self, name):
        try:
            from dateutil import parser, tz
        except ImportError:
            raise NotImplementedError()
        name = self._normalize_name(self._clean_name(name))
        entry = self.entries.get(name)
        # only call self.bucket.get_key() if the key is not found
        # in the preloaded metadata.
        if entry is None:
            entry = self.bucket.get_key(self._encode_name(name))
        # convert to string to date
        last_modified_date = parser.parse(entry.last_modified)
        # if the date has no timzone, assume UTC
        if last_modified_date.tzinfo == None:
            last_modified_date = last_modified_date.replace(tzinfo=tz.tzutc())
        # convert date to local time w/o timezone
        return last_modified_date.astimezone(tz.tzlocal()).replace(tzinfo=None)

    def url(self, name):
        name = self._normalize_name(self._clean_name(name))
        if self.custom_domain:
            return "%s://%s/%s" % ('https' if self.secure_urls else 'http', self.custom_domain, name)
        else:
            return self.connection.generate_url(self.querystring_expire, method='GET', \
                    bucket=self.bucket.name, key=self._encode_name(name), query_auth=self.querystring_auth, \
                    force_http=not self.secure_urls)

    def get_available_name(self, name):
        """ Overwrite existing file with the same name. """
        if FILE_OVERWRITE:
            name = self._clean_name(name)
            return name
        return super(GoogleStorage, self).get_available_name(name)
