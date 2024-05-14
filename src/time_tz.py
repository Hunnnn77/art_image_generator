from datetime import datetime
from pytz import timezone


class Util:
    def get_time_path(self) -> str:
        now = datetime.now(timezone("UTC"))
        time_tz = "_".join(
            str(now.astimezone(timezone("Asia/Seoul")))
            .split(".")[0]
            .replace(":", "-")
            .split(" ")
        )

        return time_tz
