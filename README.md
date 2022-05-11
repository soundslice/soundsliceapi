# Soundslice Python API library

This library lets you use the [Soundslice data API](https://www.soundslice.com/help/data-api/) from Python.

## Installation

```python
pip install soundsliceapi
```

## Usage

Note: All of these methods require a Soundslice API key. Follow the [instructions here](https://www.soundslice.com/help/data-api/#apikeys) to get one.

Each method uses a Client object, which requires your API info:

```python
from soundsliceapi import Client
client = Client(APP_ID, PASSWORD)
```

Available methods are:

### create_slice(**kwargs)

Creates a slice. Note this only creates the metadata for the slice, not the notation.

```python
from soundsliceapi import Constants

client.create_slice(
    #  All fields optional.
    name='The Power of Love',

    artist='Huey Lewis and the News',

    # Slice URL is private by default.
    has_shareable_url=True,

    # Embedding is disabled by default. To enable pass 
    # EMBED_STATUS_ON_ALLOWLIST.
    embed_status=Constants.EMBED_STATUS_ON_ALLOWLIST,

    # Printing is disabled by default.
    can_print=True,

    # A string specifying the ID of the folder in which to put the slice. 
    # If you don't specify this, it will be placed in the account's root folder.
    folder_id='31045'
)
```
Returns a dictionary of slice information with the following keys:

| Key               | Example                | Notes               |
| ----------------- | ---------------------- | ------------------- |
| `"scorehash"`       | `"nyfcn"`                | The slice’s scorehash. This is a unique identifier with a maximum size of 6 characters. |
| `"url"`             | `"/slices/nyfcn/"`       | The slice’s URL on soundslice.com. Note this URL will return a 404 until the slice has notation. |
| `"embed_url"`       | `"/slices/nyfcn/embed/"` | Only included if the slice has embedding enabled. This is the URL to put in your `<iframe>`. Note this URL will return a 404 until the slice has notation. |

### delete_slice(scorehash)
Deletes a slice, including all its associated data such as recordings.

```python
client.delete_slice("scorehash")
```
Returns a dictionary of slice information with the following keys:

| Key               | Example                | Notes               |
| ----------------- | ---------------------- | ------------------- |
| `"name"`            | `"Sussudio"`             | String. The slice’s name. |
| `"artist"`          | `"Phil Collins"`         | String. The slice’s artist. Might be an empty string, but it will always exist in the JSON. |

### list_slices()

Retrieves metadata for all slices in your account. The order of slices in the result is undefined.

```python
client.list_slices()
```

Returns a dictionary of slice information with the following keys:

| Key               | Example                | Notes               |
| ----------------- | ---------------------- | ------------------- |
| `"scorehash"`       | `"nyfcn"`                | This is a unique identifier with a maximum size of 6 characters. |
| `"url"`             | `"/slices/MpYDc/"`       | String. The slice’s URL on soundslice.com. Note this URL will return a 404 if the slice has no notation. |
| `"name"`            | `"Take Me Home Tonight"` | String. The slice’s name. |
| `"artist"`          | `"Eddie Money"`          | String. The slice’s artist. Might be an empty string, but it will always exist in the JSON. |
| `"status"`          | `1`                      | Integer. The slice’s secret URL status. <ul><li>`1` — Secret URL is disabled (default value, if not provided)</li><li>`3` — Secret URL is enabled</li></ul> |
| `"embed_status"`    | `1`                      | Integer. The slice’s embed status. <ul><li>`1` — Disabled (default value, if not provided)</li><li>`4` — Enabled on allowlist domains</li></ul>
| `"can_print"`       | `False`                  | Boolean. Whether the slice can be printed. |
| `"has_notation"`    | `True`                   | Boolean.  Whether the slice has notation. |
| `"show_notation"`   | `True`                   | Boolean. Whether the slice can show its notation. This is true except when you’ve manually disabled notation for the slice, in the slice manager. |
| `"recording_count"` | `3`                      | Integer. The number of recordings the slice has. |
| `"embed_url"`       | `"/slices/d8sDc/embed/"` | String. The slice’s embed URL. Note this URL will return a 404 if the slice has no notation, and this key will not exist in the JSON if the slice cannot be embedded. |

### get_slice(scorehash)

Retrieves metadata for a slice. On success, returns a dictionary with the same keys as documented in the list_slices() method.

```python
client.get_slice("scorehash")
```

### get_original_slice_notation_file(scorehash)

Retrieves the original notation file for a slice. This is a file in one of our supported formats (e.g., MusicXML, GPX, etc.). If you’ve uploaded multiple files, this returns the most recently uploaded file.

```python
client.get_original_slice_notation_file('scorehash')
```

On success returns in a dictionary with the following key:

| Key               | Example                                                                   | Notes               |
| ----------------- | ------------------------------------------------------------------------  | ------------------- |
| `"url"`             | `"https://soundslice-data.s3.amazonaws.com/json/592129/rawscore?response…"` | This is a URL where you can download the original notation file within the next 15 minutes.<br /><br />Note `"url"` will be set to the empty string for slices that don’t have an original notation file. |

### upload_slice_notation(**kwargs)

Uploads a notation file into a given slice.

This API method is only available by special permission. If you’d like access, <a href="https://www.soundslice.com/contact/">contact us</a> and tell us how you intend to use it.

```python
client.upload_slice_notation(
    scorehash="n4nrf", 

    # File-like object containing the raw notation data.
    fp=open("~/tmp/notation/score.xml", "r"),

    # An optional URL that Soundslice will POST to when the upload is processed. 
    # Should be a full path, starting with http:// or https://.
    callback_url=None
)
```

If a `callback_url` is provided, we’ll notify you when the upload has processed via making a POST to your specified URL. These POST requests will include these keys:

| Key               | Example                             | Notes               |
| ----------------- | ----------------------------------- | ------------------- |
| `"scorehash"`      | `"d8sDc"`                             | String. The newly created slice’s scorehash. |
| `"success"`         | `"1"`                                 | String. `"1"` if it was successfully processed. `"2"` if there was an error. |
| `"error"`           | `"We couldn't parse the given file."` | String. An error message, in case of errors. |

### move_slice_to_folder(**kwargs)

Moves a slice to a given folder, in either your own account or an organization you belong to.

```python
client.move_slice_to_folder(
    # Required scorehash
    scorehash="n4nrf",

    # Required ID of the new folder. 
    # Use folder_id 0 (zero) to move the slice to your account’s root folder.
    folder_id=0,
)
```

On success, returns in a dictionary with the following key:

| Key     | Example | Notes   |
| ------- | ------- | ------- |
| `"id"`    | `0`       | Integer. The ID of the folder, or `0` (zero) for the root folder. |

### duplicate_slice(scorehash)

Duplicates a slice, which must live within your account. The newly created slice will live in the top level of your slice manager.

```python
client.duplicate_slice("scorehash")
```

Here’s what’s duplicated:
- Title and metadata (except for creation date)
- Notation data
- All recordings
- All syncpoints

Slice version history is not duplicated.

You’ll get an immediate response with the newly created slice’s information. Please note that the notation, recordings and syncpoints might not have been yet copied at that point; it could take a few seconds, depending on the current load of our message queue.

On success, returns a dictionary with the same keys as documented in the `create_slice()` method.

### create_recording(**kwargs)

Creates a recording.

```python
from soundsliceapi import Constants

client.create_recording(
    # Required scorehash.
    scorehash="n4nrf",

    # Required. Pass one of the following constants:
        # Constants.SOURCE_MP3_UPLOAD
        # Constants.SOURCE_VIDEO_UPLOAD
        # Constants.SOURCE_VIDEO_URL
        # Constants.SOURCE_MP3_URL
        # Constants.SOURCE_YOUTUBE
        # Constants.SOURCE_VIMEO
        # Constants.SOURCE_WISTIA
    source=Constants.SOURCE_YOUTUBE,
    
    # Required for some sources. See table below.
    source_data="dQw4w9WgXcQ",

    # Applicable only if source is Constants.SOURCE_VIDEO_URL.
    # The value is not required if you provide source_data. 
    # You can provide both hls_url and source_data; in that case,
    # our player will use the hls_url for users whose 
    # browsers support HLS and source_data otherwise.
    hls_url=None,

    # Required if source is Constants.SOURCE_MP3_UPLOAD
    # or Constants.SOURCE_VIDEO_UPLOAD.
    filename=None
)
```

The `source_data` value is different depending on the recording source, as follows:

| If source is...       | Example source_data | Notes |
| --------------------- | -------------- | ----- |
| `SOURCE_YOUTUBE`      | `"dQw4w9WgXcQ"` | The URL or ID of the YouTube video. Required. |
| `SOURCE_VIDEO_URL`    | `"https://www.rmp-streaming.com/media/big-buck-bunny-360p.mp4"` | The URL of the video. Either this or `hls_url` is required. (You can also provide both.) |
| `SOURCE_VIMEO` | `"253989945"` | The ID of the Vimeo video. Required. |
| `SOURCE_WISTIA` | `"j38ihh83m5"` | The ID of the Wistia video. Required. |
| `SOURCE_MP3_URL` | `"https://stream.thisamericanlife.org/31/31.mp3"` | The URL of the MP3. Required. |

### get_slice_recordings(scorehash)

Gets data about all recordings in a given slice. On success, returns in a dictionary with the following keys:

| Key                | Example                             | Notes               |
| ------------------ | ----------------------------------- | ------------------- |
| `"id"`               | `626940`                              | The recording's ID. |
| `"name"`             | `"Video"`                             | The recording’s name. |
| `"source"`           | `1`                                   | The recording’s `source` (see above for details). |
| `"source_data"`      |  `"eBG7P-K-r1Y"`                      | The recording’s `source data` (see above for details). |
| `"hls_url"`          | `""`                                  | The recording’s HLS URL, or an empty string. |
| `"cropped_duration"` | `289.0`                               | The recording’s duration, in seconds, taking cropping into account. (For example, if the raw recording is 60 seconds long but you’ve cropped it to remove the first 10 seconds, `cropped_duration` will be `50`.) This will be set to `null` for recordings that don’t have a duration, such as recordings that are still being processed. |
| `"syncpoint_count"`  | `8`                                   | The recording’s number of syncpoints. |
| `"status"`           | `"ready"`                             | The recording’s status. The possible values are: <ul><li>`waiting` — waiting for media to be uploaded</li><li>`processing` — processing uploaded media</li><li>`ready` — ready</li><li>`error` — encountered processing error</li></ul>

### reorder_slice_recordings(**kwargs)

Sets the order of the recordings in a slice.

```python
client.reorder_slice_recordings(
    scorehash="78sDc",

    # A string of recording IDs separated by commas, in your requested order.
    # The first recording ID is the top-most recording in the Soundslice UI, 
    # and so forth. The last recording ID is the default. Every recording in 
    # the slice must be included in this data.
    order="123,124,121"
)
```

On success, the result will be an empty JSON object.

### change_recording(**kwargs)

Changes metadata for a recording.

```python
client.change_recording(
    # All are optional; if you don’t want to change a particular value, simply
    # don’t send its key with the request.
    name="YouTube performance",

    # Only available for video URLs and audio URLs.
    source_data="IuUwyIPSgnQ",

    # Only available for video URLs.
    hls_url=""
)
```

On success, returns in a dictionary with the following keys:

| Key                | Example                             | Notes               |
| ------------------ | ----------------------------------- | ------------------- |
| `"id"`               | `626940`                          | The recording's ID. |
| `"name"`             | `"YouTube performance"`           | The recording’s name. |
| `"source_data"`      |  `"IuUwyIPSgnQ"`                  | The recording’s `source data` (see above for details). |
| `"hls_url"`          | `""`                              | The recording’s HLS URL, or an empty string. |

### delete_recording(recording_id)

Deletes a recording, including all its associated data such as syncpoints and uploaded audio.

```python
client.delete_recording("626940")
```
On success, returns in a dictionary with the following key:

| Key       | Example | Notes   |
| --------- | ------- | ------- |
| `"name"`    | `"Video"` | String. The recording's name. |

### get_recording_syncpoints(recording_id)

Retrieves the syncpoints for a recording.

```python
client.get_recording_syncpoints("626940")
```
On success, returns a JSON list representing the syncpoints. See <a href="https://www.soundslice.com/help/data-api/#syncpointdata">syncpoint data format</a>.

### put_recording_syncpoints(**kwargs)

Sets the syncpoints for a recording.

```python
client.put_recording_syncpoints(
    # Required.
    recording_id="626940",

    # Required. See syncpoint data format link above.
    syncpoints=[[0, 0], [1, 0.57], [1, 0.8, 240], [2, 1.3]],

    # Optional. Number of seconds into the recording to start cropping 
    # (a float). For example, if this is 12, then the recording will begin 
    #  playback at 12 seconds, and seconds 0-12 will be inaccessible.
    crop_start=12,

    # Optional. Number of seconds into the recording to end cropping 
    # (a float). For example, if this is 60, then the recording will end 
    #  playback at the timecode 60 seconds, and any audio after timecode 60 
    # seconds will be inaccessible. Note this is relative to the absolute 
    # recording, so crop_start has no effect on crop_end.
    crop_end=60
)
```

On success, returns in a dictionary with the following key:

| Key     | Example | Notes   |
| ------- | ------  | ------- |
| `"id"`    | `626940`  | The recording ID, as an integer. |

### create_folder(**kwargs)

Creates a folder within your account’s slice manager.

```python
client.create_folder(
    # Required.
    name="Practice list",

    # Optional. The folder’s parent ID. Use this if you want to nest a folder 
    # within another one.
    parent_id=31043
)
```

On success returns in a dictionary with the following key:

| Key     | Example | Notes   |
| ------- | ------  | ------- |
| `"id"`    | `31044`  | The ID of the newly created folder. |

### rename_folder(**kwargs)

Renames the given folder within your account’s slice manager.

```python
# All required.
folder_id=31044,

name="New practice list"
```

On success, returns in a dictionary with the following key:

| Key     | Example | Notes   |
| ------- | ------  | ------- |
| `"id"`    | `31044`  | The ID of the folder. |

### delete_folder(folder_id)

Deletes the given folder within your account’s slice manager.

```python
client.delete_folder(
    folder_id=31044
)
```

On success, returns in a dictionary with the following key:

| Key         | Example | Notes   |
| ----------- | ------  | ------- |
| `"parent_id"` | `31043`   | The ID of the deleted folder’s parent folder, or `None` if the deleted folder was in the root. |

### list_folders(**kwargs)

Lists all folders within your account’s slice manager.

By default, this lists only the top-level folders. To list subfolders within a given folder, pass the parameter `parent_id`.

```python
client.list_folders(
    # Optional.
    parent_id=None
)
```
