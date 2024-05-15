import asyncio

from src.cloud import Cloud
from src.file import File
from src.time_tz import Util

import os
from dotenv import load_dotenv


async def main():
    load_dotenv(dotenv_path=f"{os.getcwd()}/.env")
    util = Util()
    f = File(util)
    await f.main()
    if len(os.listdir(f"{os.getcwd()}/backup")) == 0:
        print("Empty Output!")
        return
    c = Cloud(util)
    await c.main()


if __name__ == "__main__":
    asyncio.run(main())
