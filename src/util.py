import os
from collections import defaultdict
from datetime import datetime

from dotenv import load_dotenv
from pytz import timezone

CWD = os.getcwd()


class Util:
    @classmethod
    def load(cls):
        load_dotenv(f"{os.getcwd()}/@secret/.env")

    @staticmethod
    def get_envs(key: str) -> str:
        vals = ["ID", "CLOUD_NAME", "API_KEY", "API_SECRET", "MONGO"]
        d = defaultdict()
        for v in vals:
            if v in d:
                continue
            else:
                d[v] = os.getenv(key)
        return d[key]

    @staticmethod
    def get_time_tz(date_time: datetime | None = None) -> str:
        now = datetime.now(timezone("UTC")) if date_time is None else date_time.now(timezone("UTC"))
        time_tz = "_".join(
            str(now.astimezone(timezone("Asia/Seoul")))
            .split(".")[0]
            .replace(":", "-")
            .split(" ")
        )

        return time_tz
