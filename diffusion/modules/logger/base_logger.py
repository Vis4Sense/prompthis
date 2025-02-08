import os
import json


class ThreadLogger:
    def __init__(self):
        pass


class BaseLogger:
    def __init__(self, mode, directory, files, **kwargs) -> None:
        self.mode = mode
        self.directory = directory
        self.files = files

    def __str__(self) -> str:
        if self.mode == "one":
            files = self.files["filename"]
        elif self.mode == "list":
            files = [file["filename"] for file in self.files]
        return (
            f"BaseLogger("
            f"mode={self.mode}, "
            f"directory={self.directory}, "
            f"files={files}"
            f")"
        )

    def write(self):
        if self.files is None:
            return
        elif self.mode == "one":
            self.write_one(self.files)
        elif self.mode == "list":
            self.write_many(self.files)
        else:
            raise NotImplementedError

    def write_one(self, file):
        if type(file) is not dict:
            print(file)

        filename = file["filename"]
        _, suffix = os.path.splitext(filename)

        if suffix == ".json":
            self.write_json(file)

    def write_many(self, files):
        for file in files:
            self.write_one(file)

    def write_json(self, file):
        file_path = os.path.join(self.directory, file["filename"])
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(file["data"], f, indent=4, ensure_ascii=False)
