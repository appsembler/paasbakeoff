import urllib

import boto

from boto.exception import BotoClientError


def check_lowercase_bucketname(n):
    if not (n + 'a').islower():
        raise BotoClientError("Bucket names cannot contain upper-case " \
            "characters when using either the sub-domain or virtual " \
            "hosting calling format.")
    return True


def assert_case_insensitive(f):
    def wrapper(*args, **kwargs):
        if len(args) == 3 and check_lowercase_bucketname(args[2]):
            pass
        return f(*args, **kwargs)
    return wrapper


class _CallingFormat(object):

    def get_bucket_server(self, server, bucket):
        return ''

    def build_url_base(self, connection, protocol, server, bucket, key=''):
        url_base = '%s://' % protocol
        url_base += self.build_host(server, bucket)
        url_base += connection.get_path(self.build_path_base(bucket, key))
        return url_base

    def build_host(self, server, bucket):
        if bucket == '':
            return server
        else:
            return self.get_bucket_server(server, bucket)

    def build_auth_path(self, bucket, key=''):
        key = boto.utils.get_utf8_value(key)
        path = ''
        if bucket != '':
            path = '/' + bucket
        return path + '/%s' % urllib.quote(key)

    def build_path_base(self, bucket, key=''):
        key = boto.utils.get_utf8_value(key)
        return '/%s' % urllib.quote(key)


class SubdomainCallingFormat(_CallingFormat):

    @assert_case_insensitive
    def get_bucket_server(self, server, bucket):
        return '%s.%s' % (bucket, server)
