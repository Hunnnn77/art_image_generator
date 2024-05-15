import asyncio

from src.cloud import Cloud
from src.file import File
from src.time_tz import Util

from dotenv import load_dotenv


async def main():
    load_dotenv()
    util = Util()
    f = File(util)
    await f.main()
    c = Cloud(util)
    await c.main()


if __name__ == "__main__":
    asyncio.run(main())
