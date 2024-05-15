import asyncio
import os

from src.cloud import Cloud
from src.file import File
from src.time_tz import Util

from dotenv import load_dotenv


async def main():
    load_dotenv()
    util = Util()
    f = File(util)
    c = Cloud(util)
    _ = await f.main()
    if len(os.listdir(f"{os.getcwd()}/input")) == 0:
        return
    _ = await c.main()


if __name__ == "__main__":
    asyncio.run(main())
