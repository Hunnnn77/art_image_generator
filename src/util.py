from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from pytz import timezone
import os

CWD = os.getcwd()


class Util:
    @classmethod
    def load(cls):
        load_dotenv(f"{os.getcwd()}/@secret/.env")

    def get_envs(self, key: str) -> str:
        vals = ["ID", "CLOUD_NAME", "API_KEY", "API_SECRET"]
        d = defaultdict()
        for v in vals:
            if v in d:
                continue
            else:
                d[v] = os.getenv(key)
        return d[key]

    def get_time_tz(self) -> str:
        now = datetime.now(timezone("UTC"))
        time_tz = "_".join(
            str(now.astimezone(timezone("Asia/Seoul")))
            .split(".")[0]
            .replace(":", "-")
            .split(" ")
        )

        return time_tz
