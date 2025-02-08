import os
import pytz
import pandas as pd

from datetime import datetime
from pydantic import BaseModel, Field

from .creation_logger import CreationLogger


class SessionLogLine(BaseModel):
    session_id: int = Field(title="Session ID")
    session_name: str = Field(title="Session name")
    create_time: datetime = Field(..., title="Creation time")
    create_timezone: str = Field(default="Asia/Shanghai", title="Creation timezone")
    update_time: datetime = Field(default=None, title="Update time")
    update_timezone: str = Field(default=None, title="Update timezone")


class SessionLogger:
    def __init__(
        self,
        user_id: int = None,
        log_dir: str = "./outputs",
    ) -> None:
        self.user_id = user_id

        # session log directory
        if user_id is None:
            session_dir = os.path.join(log_dir, "cache")
            print("Warning: user_id is None, the log will be saved in cache directory.")
        else:
            session_dir = os.path.join(log_dir, f"{user_id}")

        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        self.log_dir = log_dir
        self.session_log_path = os.path.join(session_dir, "log.csv")

    def fetch_session_list(self):
        if not os.path.exists(self.session_log_path):
            return []

        df = pd.read_csv(self.session_log_path)
        return df.to_dict(orient='records')

    def log_session(self):
        # create session log file if not exists
        if not os.path.exists(self.session_log_path):
            columns = SessionLogLine.model_json_schema()["properties"].keys()
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.session_log_path, index=False)

        # get new session id
        df = pd.read_csv(self.session_log_path)
        session_id = df.shape[0] if df.shape[0] > 0 else 0

        # save session log line
        timezone_name = 'Asia/Shanghai'
        create_time = datetime.now(pytz.timezone(timezone_name))
        create_time_str = create_time.strftime("%Y-%m-%d %H:%M:%S")

        data = {
            'session_id': session_id,
            'session_name': f'Session {session_id}',
            'create_time': create_time_str,
            'create_timezone': timezone_name,
            'update_time': create_time_str,
            'update_timezone': timezone_name,
        }

        session_info = SessionLogLine(**data).model_dump()
        new_row = pd.DataFrame([session_info])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(self.session_log_path, index=False)

        session_dir = os.path.join(self.log_dir, str(self.user_id), str(session_id))
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        creation_logger = CreationLogger(
            user_id=self.user_id,
            thread_id=session_id,
            log_dir=self.log_dir,
        )
        creation_logger.init_log_file()

        return pd.read_csv(self.session_log_path).to_dict(orient='records')
