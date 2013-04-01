import urllib
from django.utils.encoding import smart_str
from django.http import HttpResponse
from google.appengine.ext import blobstore
from google.appengine.ext.blobstore import BLOB_KEY_HEADER


def file_serve(request, filename):

    blobinfo = blobstore.BlobInfo.all().filter('filename =', filename)
    blobstore_key = blobinfo[0].key()._BlobKey__blob_key

    blob_info = blobstore.BlobInfo.get(blobstore_key)

    filename = getattr(blob_info, 'filename', blobstore_key)
    content_type = getattr(blob_info, 'content_type', 'application/octet-stream')

    response = HttpResponse(content_type=content_type)
    response[BLOB_KEY_HEADER] = blobstore_key

    response['Content-Disposition'] = smart_str(
        u'attachment; filename=%s' % filename.split('/')[-1]
    )

    return response