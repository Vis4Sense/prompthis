# Translators

Translate DSL to local API

## DSL

Preprocess: image encoding

```json
{
    "extension_name": "preprocess",
    "task": "image_encoding",
    "url": "",
    "data": { "object": "thread", "user_id": 0, "thread_id": 0 },
    "input": [
        {
            "attribute": "log/image",
            "filter": "unprocessed" // unprocessed | latest | all
        }
    ],
    "output": "map-log/image"
}
```

Preprocess: image projection

```json
{
    "extension_name": "preprocess",
    "task": "image_projection",
    "url": "",
    "data": { "object": "thread", "user_id": 0, "thread_id": 0 },
    "input": [
        {
            "attribute": "preprocess/image_encoding",
            "filter": "all"
        },
        {
            "attribute": "preprocess/image_projection",
            "filter": "latest"
        }
    ],
    "output": "latest-log/prompt"
}
```

## API

```json
{
    "mode": "list" /** list or one */,
    "directory": "",
    "filenames": [] /** list, str, or None */
}
```
