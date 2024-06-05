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
        """1: gen image(original x 300 x 60 -> google_sheet)
2: gen portfolio(by date)
3: gen reference(by folder_name you designated)
4: gen press(all)
5: gen json(SHEET!seed -> figma)\n\t[WARN]\n\t- urls + detailed information(materials, years ..)\n""")
    try:
        match int(user_input):
            case 1:
                await f.parse_original()
                if len(os.listdir(f"{os.getcwd()}/_backup")) == 0:
                    raise Exception("Nothing Generated!")
                await c.parse_original()
            case 2:
                await f.parse_portfolio()
                await c.parse_portfolio()
            case 3:
                await f.parse_reference()
                await c.parse_references()
            case 4:
                f.parsing_text()
            case 5:
                c.generating_json()
                raise ValueError("Invalid command")
            case _:
                raise NotImplementedError("Unknown command")

    except Exception as e:
        raise e


if __name__ == "__main__":
    asyncio.run(main())
