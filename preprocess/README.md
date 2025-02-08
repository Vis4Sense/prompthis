# Preprocess

Preprocess is an extension of the [diffusion](https://github.com/prompt-vis/diffusion) app.

The app receives requests specifying preprocessing tasks and input data and responses with processed data.
The tasks, input, and output are determined through predefined [configuration](#configuration), which is part of the [request](#request-and-response-format).

Current preprocessing modules include [image encoding](#image-encoding) and [image projection](#image-projection).
The modules can be extended to include more preprocessing methods.

## Configuration

Example configuration

```yaml
- name: preprocess
    task: image_encoding
    url: http://127.0.0.1:5707/image_encoding
    trigger: text2image_creation
    trigger_time: post_request
    trigger_order: 1
    input:
        - attribute: log/image
        filter: unprocessed
    output: map-log/image-json
- name: preprocess
    task: image_projection
    url: http://127.0.0.1:5707/image_projection
    trigger: text2image_creation
    trigger_time: post_request
    trigger_order: 2
    input:
        - attribute: preprocess/image_encoding
        filter: all
        - attribute: preprocess/image_projection
        filter: latest
    output: latest-log/prompt-json
```

## Request and Response Format

Request

```json
{
    "input": {
        "{attribute}": {
            "filter": "{filter_name}",
            "data": []
        },
        "{attribute}": {}
    },
    "config": {} /** see extension configuration file in diffusion app */
}
```

Response

```json
{
    "output": [],
    "config": {} /** same with request */
}
```

## Image Encoding

Currently use the image encoder of [CLIP](https://github.com/openai/CLIP) to embed the images. See [image encoder processor](./modules/image_encoding_processor.py) for details of implementation.

Request

```json
{
    "input": {
        "log/image": {
            "filter": "unprocessed",
            "data": [
                {
                    "filename": "93(0).png",
                    "data": "base64_image_data"
                },
                {}
            ]
        }
    },
    "config": {}
}
```

Response

```json
{
    "output": [
        {
            "filename": "{filename}" /** same with request */,
            "data": [] /** embedding */
        },
        {}
    ] /** map input image data to image embeddings */,
    "config": {}
}
```

## Image Projection

Currently use t-SNE to calculate the image projection.

When new images are generated, the new projection is aligned with the previous one via [procrustes algorithm](https://en.wikipedia.org/wiki/Orthogonal_Procrustes_problem).
The [spicy package](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.procrustes.html) provides an implementation of this algorithm.
Here, the implemented function is slightly modified in the [image projection processor](./modules/image_projection_processor.py) to include the transformation matrix in the return values, so that it can be applied to new data points.

Request

```json
{
    "input": {
        "preprocess/image_encoding": {
            "filter": "all",
            "data": [
                {
                    "filename": "2(0).json",
                    "data": [0.2032470703125, ...]
                },
                {}
            ],
        },
        "preprocess/image_projection": {
            "filter": "latest",
            "data": ""
        }
    },
    "config": {}
}
```

Response

```json
{
    "output": {
        "{filename}": [] /** projection */,
        "{filename}": []
    } /** projection */,
    "config": {}
}
```
