"""The official Python library for Soundslice's data API."""

__version__ = '1.1'

import json
import requests

class Constants:
    # Constants for the user to import and pass.
    EMBED_STATUS_ON_ALLOWLIST = 4
    # Constants for recording upload.
    SOURCE_MP3_UPLOAD = 2
    SOURCE_VIDEO_UPLOAD = 4
    SOURCE_VIDEO_URL = 3
    SOURCE_MP3_URL = 8
    SOURCE_YOUTUBE = 1
    SOURCE_VIMEO = 6
    SOURCE_WISTIA = 7

# Internal constants used by the API.
METHOD_POST = 1
METHOD_GET = 2
METHOD_DELETE = 3
PRINT_STATUS_ALLOWED = 3
STATUS_URL_SHAREABLE = 3
LINKED_SOURCES = [
    Constants.SOURCE_YOUTUBE,
    Constants.SOURCE_VIMEO,
    Constants.SOURCE_WISTIA,
    Constants.SOURCE_MP3_URL
]

class PermissionDenied(Exception):
    pass

class ValidationError(Exception):
    def __init__(self, msg):
        self.msg = msg

class RateLimited(Exception):
    pass

class Client:
    API_PREFIX = 'https://www.soundslice.com/api/v1'

    def __init__(self, app_id, password):
        self.app_id = app_id
        self.password = password

    def make_request_raw(self, method, endpoint, data=None):
        url = f'{self.API_PREFIX}{endpoint}'
        auth = (self.app_id, self.password)
        if method == METHOD_POST:
            response = requests.post(url, auth=auth, data=data)
        elif method == METHOD_GET:
            response = requests.get(url, auth=auth)
        elif method == METHOD_DELETE:
            response = requests.delete(url, auth=auth)
        status_code = response.status_code
        if status_code == 403:
            raise PermissionDenied
        elif status_code == 422:
            raise ValidationError(response.content)
        elif status_code == 429:
            raise RateLimited
        return response

    def make_request(self, method, endpoint, data=None):
        response = self.make_request_raw(method, endpoint, data=data)
        return response.json()

    def create_slice(self, name=None, artist=None, has_shareable_url=False, embed_status=None, can_print=False, folder_id=None):
        data = {}
        if name is not None:
            data['name'] = name
        if artist is not None:
            data['artist'] = artist
        if has_shareable_url:
            data['status'] = STATUS_URL_SHAREABLE
        if embed_status is not None:
            data['embed_status'] = embed_status
        if can_print:
            data['print_status'] = PRINT_STATUS_ALLOWED
        if folder_id is not None:
            data['folder_id'] = folder_id
        return self.make_request(METHOD_POST, '/slices/', data=data)

    def delete_slice(self, scorehash):
        return self.make_request(METHOD_DELETE, f'/slices/{scorehash}/')

    def list_slices(self):
        return self.make_request(METHOD_GET, '/slices/')

    def get_slice(self, scorehash):
        return self.make_request(METHOD_GET, f'/slices/{scorehash}/')

    def get_original_slice_notation_file(self, scorehash):
        response = self.make_request(METHOD_GET, f'/slices/{scorehash}/notation-file/')
        return response['url']

    def upload_slice_notation(self, scorehash, fp, callback_url=None):
        data = None
        if callback_url:
            data = {'callback_url': callback_url}
        response = self.make_request(METHOD_POST, f'/slices/{scorehash}/notation-file/', data=data)
        requests.put(response['url'], data=fp)

    def get_slice_musicxml(self, scorehash):
        response = self.make_request_raw(METHOD_GET, f'/slices/{scorehash}/musicxml/')
        if response.status_code == 404:
            return None
        return response.text

    def move_slice_to_folder(self, scorehash, folder_id=None):
        # folder_id 0 is the user's top-level folder. We accept None in this library as syntactic sugar.
        if folder_id is None:
            folder_id = 0
        return self.make_request(METHOD_POST, f'/slices/{scorehash}/move/', data={'folder_id': folder_id})

    def duplicate_slice(self, scorehash):
        return self.make_request(METHOD_POST, f'/slices/{scorehash}/duplicate/')

    def create_recording(self, scorehash, source, name=None, source_data=None, hls_url=None, filename=None):
        url = f'/slices/{scorehash}/recordings/'
        data = {'source': source}
        if name is not None:
            data['name'] = name
        if source in LINKED_SOURCES:
            data['source_data'] = source_data
            return self.make_request(METHOD_POST, url, data=data)
        elif source == SOURCE_VIDEO_URL:
            if source_data:
                data['source_data'] = source_data
            if hls_url:
                data['hls_url'] = hls_url
            return self.make_request(METHOD_POST, url, data=data)
        elif source == SOURCE_MP3_UPLOAD or source == SOURCE_VIDEO_UPLOAD:
            # First create the recording.
            response = self.make_request(METHOD_POST, url, data=data)
            # Get a temporary URL to PUT media.
            response = self.make_request(METHOD_POST, f"/recordings/{response['id']}/media/")
            return requests.put(response['url'], data=open(filename, 'rb'))

    def get_slice_recordings(self, scorehash):
        return self.make_request(METHOD_GET, f'/slices/{scorehash}/recordings/')

    def reorder_slice_recordings(self, scorehash, order):
        return self.make_request(
            METHOD_POST,
            f'/slices/{scorehash}/recordings/order/',
            data={'order': order}
        )

    def change_recording(self, recording_id, name=None, source_data=None, hls_url=None):
        data = {}
        if name:
            data['name'] = name
        if source_data:
            data['source_data'] = source_data
        if hls_url:
            data['hls_url'] = hls_url
        return self.make_request(METHOD_POST, f'/recordings/{recording_id}/', data=data)

    def delete_recording(self, recording_id):
        return self.make_request(METHOD_DELETE, f'/recordings/{recording_id}/')

    def get_recording_syncpoints(self, recording_id):
        return self.make_request(METHOD_GET, f'/recordings/{recording_id}/syncpoints/')

    def put_recording_syncpoints(self, recording_id, syncpoints, crop_start=None, crop_end=None):
        data = {'syncpoints': syncpoints}
        if crop_start:
            data['crop_start'] = crop_start
        if crop_end:
            data['crop_start'] = crop_end
        return self.make_request(METHOD_POST, f'/recordings/{recording_id}/syncpoints/', data=data)

    def create_folder(self, name, parent_id=None):
        data = {'name': name}
        if parent_id:
            data['parent_id'] = parent_id
        return self.make_request(METHOD_POST, '/folders/', data=data)

    def rename_folder(self, folder_id, name):
        data = {'name': name}
        return self.make_request(METHOD_POST, f'/folders/{folder_id}/', data=data)

    def delete_folder(self, folder_id):
        return self.make_request(METHOD_DELETE, f'/folders/{folder_id}/')

    def list_folders(self, parent_id=None):
        if parent_id:
            url = f'/folders/?parent_id={parent_id}'
        else:
            url = '/folders/'
        return self.make_request(METHOD_GET, url)
