import asyncio
import os

from src.cloud import Cloud
from src.file import File
from src.util import Util


async def main():
    Util.load()
    util = Util()
    # f = File(util)
    # await f.main()
    # if len(os.listdir(f"{os.getcwd()}/_backup")) == 0:
    #     raise Exception("Nothing Generated!")
    c = Cloud(util)
    await c.main()


if __name__ == "__main__":
    asyncio.run(main())
