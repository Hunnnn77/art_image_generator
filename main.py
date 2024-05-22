import asyncio
import os

from src.cloud import Cloud
from src.file import File
from src.util import Util


async def main():
    user_input = input("1 or 2?\n")
    Util.load()
    util = Util()

    try:
        sheet_id = input("sheet Id?\n")
        if sheet_id == "":
            print(
                "[WARN] `sheet_id` is empty, may error when you already copied original file"
            )
        match int(user_input):
            case 1:
                f = File(util)
                await f.main()
                if len(os.listdir(f"{os.getcwd()}/_backup")) == 0:
                    raise Exception("Nothing Generated!")
                c = Cloud(util, sheet_id)
                await c.main()
            case 2:
                c = Cloud(util, sheet_id)
                c.main2()
            case _:
                raise ValueError("Invalid command")
    except Exception as e:
        raise e


if __name__ == "__main__":
    asyncio.run(main())
