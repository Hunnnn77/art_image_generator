import asyncio
import os

from src.file import File
from src.net.cloud import Cloud
from src.util import Util


async def main():
    Util.load()
    util = Util()
    f = File(util)
    f.initialize()
    sheet_id = input(
        "sheet_id?\n\t[example] https://docs.google.com/spreadsheets/d/\"YOUR_SHEET_ID\"/edit#...\n")
    if sheet_id == "":
        print(
            "[WARN] `sheet_id` is empty, urls will be placed in ORIGINAL!CURRENT_DATE\n"
        )

    c = Cloud(util, sheet_id)

    user_input = input(
        """1: raw_images to google_sheet\n2: generating json\n\t[WARN]\n\t- urls should be in SHEET!seed\n\t- fill detailed information(materials, years ..) for pieces\n3: tagged_images to database\n4: parsing press urls via txt file\n(Select 1 to 4)\n""")
    try:
        match int(user_input):
            case 1:
                await f.parse_original()
                if len(os.listdir(f"{os.getcwd()}/_backup")) == 0:
                    raise Exception("Nothing Generated!")
                await c.parse_original()
            case 2:
                c.generating_json()
                raise ValueError("Invalid command")
            case 3:
                await f.parse_tagged()
                await c.parse_tagged()
            case 4:
                f.parsing_text()
            case _:
                raise NotImplementedError("Unknown command")

    except Exception as e:
        raise e


if __name__ == "__main__":
    asyncio.run(main())
