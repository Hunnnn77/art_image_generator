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
    f.init()
    f.parser.extract_from_pptx()
    f.parser.extract_from_pdf()
    if len(os.listdir(f"{os.getcwd()}/input")) == 0:
        return
    await f.main()

    c = Cloud(util=util)
    await c.main()


if __name__ == "__main__":
    asyncio.run(main())
