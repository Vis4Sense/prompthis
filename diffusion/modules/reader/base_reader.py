import os
import io
import json
import base64
import pandas as pd
from PIL import Image
from .readers import register_reader


@register_reader("base")
class BaseReader:
    def __init__(self, mode, directory, filenames, **kwargs) -> None:
        self.mode = mode
        self.directory = directory
        self.filenames = filenames

    def __str__(self) -> str:
        return (
            f"BaseReader("
            f"mode={self.mode}, "
            f"directory={self.directory}, "
            f"filenames={self.filenames}"
            f")"
        )

    def read(self, preview=False):
        if self.filenames is None:
            return None
        if self.mode == "one":
            return self.read_one(self.filenames, preview=preview)
        return self.read_many(self.filenames, preview=preview)

    def read_one(self, filename, preview=False) -> dict or list or str:
        segs = filename.split(".")
        suffix = segs[-1]

        if suffix == "csv":
            return self.read_csv(filename)
        elif suffix == "png":
            return self.read_image(filename, preview=preview)
        elif suffix == "json":
            return self.read_json(filename)
        raise NotImplementedError

    def read_many(self, filenames, preview=False) -> list:
        return [{
            "filename": filename,
            "data": self.read_one(filename, preview) 
        } for filename in filenames]

    def read_csv(self, filename) -> list:
        filepath = os.path.join(self.directory, filename)
        df = pd.read_csv(filepath)

        def row_dropna(row):
            row = row.dropna()
            return row

        def row_parse_json(row):
            for key, value in row.items():
                if not isinstance(value, str):
                    continue
                try:
                    value = json.loads(value)
                    row[key] = value
                except json.decoder.JSONDecodeError:
                    continue
            return row

        df = df.apply(row_dropna, axis=1)
        df = df.apply(row_parse_json, axis=1)
        return df.to_dict(orient="records")

    def read_json(self, filename) -> dict:
        filepath = os.path.join(self.directory, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.decoder.JSONDecodeError:
                print(f"invalid json file: {filepath}")
                return {}

    def read_image(self, filename, preview=False, max_width=128, max_height=128) -> str:
        filepath = os.path.join(self.directory, filename)
        image = Image.open(filepath)

        # Convert the resized image to bytes (image stream)
        img_io = io.BytesIO()
        image.save(img_io, 'JPEG')
        img_io.seek(0)

        # Encode the image data as Base64
        image_data_base64 = base64.b64encode(img_io.getvalue()).decode()

        if not preview:
            return image_data_base64

        # Check the image dimensions
        width, height = image.size
        if width > max_width or height > max_height:
            # Resize the image if it's larger than the maximum dimensions
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            resized_image = image.resize((new_width, new_height))
        else:
            # Keep the original image if it's smaller than or equal to the maximum dimensions
            resized_image = image

        # Convert the resized image to bytes (image stream)
        img_io = io.BytesIO()
        resized_image.save(img_io, 'JPEG')
        img_io.seek(0)

        # Encode the image data as Base64
        image_data_base64 = base64.b64encode(img_io.getvalue()).decode()

        return image_data_base64
