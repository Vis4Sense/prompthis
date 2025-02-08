import io
import os
import copy
import json
import pytz
import base64
import pandas as pd
from PIL import Image
from datetime import datetime
from pydantic import BaseModel, Field, validator


class CreationLogLine(BaseModel):
    prompt_id: int = Field(title="Prompt ID")
    model: str = Field(title="Model name")
    create_time: datetime = Field(..., title="Creation time")
    create_timezone: str = Field(default="Asia/Shanghai", title="Creation timezone")
    finish_time: datetime = Field(default=None, title="Finish time")
    finish_timezone: str = Field(default=None, title="Finish timezone")
    width: int = Field(default=None, title="Image width")
    height: int = Field(default=None, title="Image height")
    steps: int = Field(default=None, title="Steps")
    batch_size: int = Field(default=None, title="Batch size")
    prompt: str = Field(title="Prompt")
    negative_prompt: str = Field(default=None, title="Negative prompt")
    setting_filename: str = Field(default=None, title="Setting filename")
    output_filenames: str = Field(default=None, title="Output filenames")
    ratings: str = Field(default=None, title="Ratings")


class CreationResponse(BaseModel):
    """The response of the creation request."""
    parameters: dict = Field(default={}, title="Parameters")
    images: list = Field(title="Images")
    info: dict = Field(default={}, title="Info")

    @validator("info", pre=True)
    def parse_json(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string")
        return v


class CreationLogger:
    def __init__(self, user_id=None, thread_id=None, log_dir = "./outputs"):
        self.user_id = user_id
        self.thread_id = thread_id

        # thread log directory
        if user_id is None:
            thread_dir = os.path.join(log_dir, "cache")
            print("Warning: user_id is None, the log will be saved in cache directory.")
        elif thread_id is None:
            thread_dir = os.path.join(log_dir, f"{user_id}", "cache")
            print("Warning: thread_id is None, the log will be saved in cache directory.")
        else:
            thread_dir = os.path.join(log_dir, f"{user_id}", f"{thread_id}")
        print(thread_dir)

        self.thread_log_path = os.path.join(thread_dir, "log.csv")
        self.thread_data_dir = os.path.join(thread_dir, "data")

        if not os.path.exists(self.thread_log_path):
            self.row_idx = 0
        else:
            df = pd.read_csv(self.thread_log_path)
            self.row_idx = df.shape[0] if df.shape[0] > 0 else 0

    def get_prompt_id(self):
        return self.row_idx

    def init_log_file(self):
        # create thread data directory if not exists
        if not os.path.exists(self.thread_data_dir):
            os.makedirs(self.thread_data_dir)

        # create thread log file if not exists
        if not os.path.exists(self.thread_log_path):
            columns = CreationLogLine.model_json_schema()["properties"].keys()
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.thread_log_path, index=False)

    def log_request(self, request_info):
        print("log request")

        # create thread data directory if not exists
        if not os.path.exists(self.thread_data_dir):
            os.makedirs(self.thread_data_dir)

        # create thread log file if not exists
        if not os.path.exists(self.thread_log_path):
            columns = CreationLogLine.model_json_schema()["properties"].keys()
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.thread_log_path, index=False)

        df = pd.read_csv(self.thread_log_path)
        row_num = df.shape[0]

        # save settings
        create_time = request_info["time"]
        create_time_str = create_time.strftime("%Y%m%d%H%M%S")
        setting_filename = f"{row_num}_{create_time_str}_settings.json"
        data_ = copy.deepcopy(request_info["data"])
        data_["prompt_id"] = row_num
        data_["model"] = request_info["model"]
        data_["create_time"] = create_time.strftime("%Y-%m-%d %H:%M:%S")
        data_["create_timezone"] = request_info["timezone"]
        data_["setting_filename"] = setting_filename
        creation_info = CreationLogLine(**data_).model_dump()

        new_row = pd.DataFrame([creation_info])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(self.thread_log_path, index=False)

        # save request as json file
        setting_filepath = os.path.join(self.thread_data_dir, setting_filename)
        request_ = copy.deepcopy(request_info)
        del request_["logger"]
        del request_["extensions"]
        request_["time"] = request_["time"].strftime("%Y-%m-%d %H:%M:%S")
        with open(setting_filepath, "w", encoding="utf-8") as f:
            json.dump({
                "request": request_
            }, f, indent=4)

        self.row_idx = row_num
        self.setting_filepath = setting_filepath

    def log_response(self, response):
        response = CreationResponse(**response).dict()
        print("log response")
        print(response.keys())

        row_idx = self.row_idx
        output_filenames = []

        # finish time
        timezone_name = "Asia/Shanghai"
        finishi_time = datetime.now(pytz.timezone(timezone_name))

        # save images
        images = response["images"]
        for idx, img in enumerate(images):
            image = Image.open(io.BytesIO(base64.b64decode(img.split(",",1)[0])))
            filename = f'{row_idx}({idx}).png'
            filepath = os.path.join(self.thread_data_dir, filename)
            image.save(filepath)
            output_filenames.append(filename)

        # save parameters and info
        with open(self.setting_filepath, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            settings["parameters"] = response["parameters"]
            settings["info"] = response["info"]
        with open(self.setting_filepath, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)

        # update log
        df = pd.read_csv(self.thread_log_path)
        info = df.iloc[row_idx].dropna().to_dict()
        info = {**info, **response["parameters"], **response["info"]}
        info["finish_time"] = finishi_time.strftime("%Y-%m-%d %H:%M:%S")
        info["finish_timezone"] = timezone_name
        info["output_filenames"] = json.dumps(output_filenames)
        info = CreationLogLine(**info).model_dump()
        df.iloc[row_idx] = info
        df.to_csv(self.thread_log_path, index=False)
