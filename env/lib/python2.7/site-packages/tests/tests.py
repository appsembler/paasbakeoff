# -*- coding: utf-8 -*-
from django.test import TestCase
from django.core.files.storage import get_storage_class
from django.core.files.base import ContentFile

from google.appengine.ext import testbed
from google.appengine.api.blobstore import blobstore_stub, file_blob_storage
from google.appengine.api.files import file_service_stub

from rocket_engine.storage import BlobStorage


class TestbedWithFiles(testbed.Testbed):

    def init_blobstore_stub(self):
        blob_storage = file_blob_storage.FileBlobStorage(
          '/tmp/testbed.blobstore',
          testbed.DEFAULT_APP_ID
        )
        blob_stub = blobstore_stub.BlobstoreServiceStub(blob_storage)
        file_stub = file_service_stub.FileServiceStub(blob_storage)
        self._register_stub('blobstore', blob_stub)
        self._register_stub('file', file_stub)


class TestBlobStorage(TestCase):

    def setUp(self):
        self.storage = BlobStorage()

        self.testbed = TestbedWithFiles()
        self.testbed.activate()
        self.testbed.init_blobstore_stub()
        self.testbed.init_datastore_v3_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_get_blobstorage_storage(self):
        self.assertEqual(
            get_storage_class('rocket_engine.storage.BlobStorage'),
            BlobStorage
        )

        self.storage = BlobStorage()

    def test_save(self):
        file_name = 'test_name'
        file_content = b'test_content'

        f_name = self.storage.save(file_name, ContentFile(file_content))

        self.assertEqual(f_name, file_name)

    def test_open(self):
        file_name = 'test_name'
        file_content = b'test_content'

        self.storage.save(file_name, ContentFile(file_content))

        f = self.storage.open(file_name)

        self.assertEqual(f.read(), file_content)

    def test_exists(self):
        file_name = 'test_name'
        file_content = b'test_content'

        self.assertFalse(self.storage.exists(file_name))

        self.storage.save(file_name, ContentFile(file_content))

        self.assertTrue(self.storage.exists(file_name))

    def test_available_name(self):
        file_name = 'test_name'
        file_content = b'test_content'

        self.storage.save(file_name, ContentFile(file_content))

        f_name_1 = self.storage.save(file_name, ContentFile(file_content))
        f_name_2 = self.storage.save(file_name, ContentFile(file_content))

        self.assertEqual(f_name_1, "%s_1" % file_name)
        self.assertEqual(f_name_2, "%s_2" % file_name)

    def test_unicode_file_names(self):
        file_name = u'¿Cómo?'
        file_content = b'test_content'

        f_name = self.storage.save(file_name, ContentFile(file_content))

        self.assertEqual(f_name, file_name)
