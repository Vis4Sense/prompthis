# Read Log Data

## DSL for Reading data

```json
{
    "metaInfo": {
        "userId": "{user_id}",
        "sessionId": "{session_id}",
    },
    "attributes": [
        {
            "attribute": "log/image",
            "fileNaming": "log/image-json", // (image | prompt) - (json)
            "filter": {
                "type": "all", // unprocessed | latest | all
                "params": { // example params for 'unprocessed'
                    "name": "preprocess",
                    "task": "image_encoding"
                },
                "strict": false, // true | false
            },
        }
    ]
}
```

## Thread Reader

`thread_reader.py`

Read data of a certain thread.

It accepts an API and reads data accordingly.

The format of the API is

```json
{
    "mode": "list" /** list or one */,
    "directory": "",
    "filenames": [] /** list, str, or None */
}
```

Possible data to read:

- log.csv
- images
- (certain) settings
- preprocessed data
  - image encodings
  - projection
  - filenames
