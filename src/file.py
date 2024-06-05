import asyncio
import os
import shutil
from pathlib import Path
from typing import Generator, Any

from src.parser.image import ImageGenerator, ImageParser
from src.parser.text import TextParser
from src.util import CWD, Util
from datetime import datetime


async def del_dir(directory: str):
    shutil.rmtree(directory, ignore_errors=True)
    if not Path(directory).exists():
        Path(directory).mkdir()


def make_dir(path: str):
    p = Path(path)
    if not p.exists():
        p.mkdir()


class File:
    Input = f"{CWD}/input"
    Portfolio = f"{CWD}/portfolio"
    Reference = f"{CWD}/reference"
    Urls = f"{CWD}/urls"
    Secret = f"{CWD}/@secret"
    Backup = f"{CWD}/_backup"
    Output = f"{CWD}/_output"
    Json = f"{CWD}/_json"
    Origin = f"{Output}/original"
    Resized = f"{Output}/resized"
    ResizedPL = f"{Output}/resizedPL"

    def __init__(self, util: Util) -> None:
        self.util = util
        self.image = ImageGenerator()
        self.image_parser = ImageParser()
        self.text_parser = TextParser(f"{File.Urls}/inputs.txt")

    @staticmethod
    def initialize():
        for v in [
            File.Secret,
            File.Input,
            File.Portfolio,
            File.Reference,
            File.Urls,
            File.Output,
            ImageParser.Pptx,
            ImageParser.Pdfs,
            File.Origin,
            File.Json,
            File.Resized,
            File.ResizedPL,
            File.Backup,
        ]:
            make_dir(v)

        has = os.listdir(Path(f"{File.Urls}"))
        if len(has) > 0:
            return
        with open(f"{File.Urls}/inputs.txt", 'w', encoding='utf-8') as f:
            f.writelines("""//engineering
//gallery
//logistics
//medical
""")

    async def generate_images(
            self, li: Generator[Path, None, None], folder_name: str = ""
    ):
        resized = ""
        pl = ""

        for i, path in enumerate(li):
            if path.is_file():
                img, size = self.image.get_image_with_size(f"{path.absolute()}")

                if "." not in path.stem:
                    resized = resized.replace(",", "-").replace("_", "-")
                    resized = (
                            path.name.split(".")[0].replace(" ", "-")
                            + "_RESIZED"
                            + path.suffix
                    )
                    pl = pl.replace(",", "-").replace("_", "-")
                    pl = path.name.split(".")[0].replace(" ", "-") + "_PL" + path.suffix
                else:
                    resized = resized.replace(",", "-").replace("_", "-")
                    resized: str = (
                            path.stem.replace(".", "_").replace(" ", "-")
                            + "_RESIZED"
                            + path.suffix
                    )
                    pl = pl.replace(",", "-").replace("_", "-")
                    pl: str = (
                            path.stem.replace(".", "_").replace(" ", "-")
                            + "_PL"
                            + path.suffix
                    )

                if len(resized) == 0:
                    raise Exception("fileN isn't captured")

                await asyncio.gather(
                    self.image.save_image(
                        image=img,
                        location=File.Origin,
                        fileName=path.name.replace(",", "-")
                        .replace(" ", "-")
                        .replace("_", "-")
                        if not folder_name
                        else folder_name + "_" + path.name.replace(",", "-")
                        .replace(" ", "-")
                        .replace("_", "-"),
                        index=i + 1,
                    ),
                    self.image.save_image(
                        image=self.image.resize_image(
                            image=img, size=size, isPLSize=False
                        ),
                        location=File.Resized,
                        fileName=resized
                        if not folder_name
                        else folder_name + "_" + resized,
                        index=i + 1,
                    ),
                    self.image.save_image(
                        image=self.image.resize_image(
                            image=img, size=size, isPLSize=True
                        ),
                        location=File.ResizedPL,
                        fileName=pl if not folder_name else folder_name + "_" + pl,
                        index=i + 1,
                    ),
                )

            else:
                nested = Path.iterdir(Path(path.absolute()))
                await self.generate_images(nested, folder_name=path.name)

    async def move_images(
            self,
    ):
        time_tz = self.util.get_time_tz()
        dest = Path(f"{File.Output}/{time_tz}")
        if not dest.exists():
            dest.mkdir()
        else:
            paths = [
                f"{dest}/origin",
                f"{dest}/resized",
                f"{dest}/resizedPLL",
                f"{dest}",
            ]

            await asyncio.gather(*(del_dir(p) for p in paths))

        async def moving(start: str):
            shutil.move(start, dest)

        await asyncio.gather(
            *(moving(p) for p in [File.Origin, File.Resized, File.ResizedPL])
        )

    async def parse_original(self) -> None:
        print("Parsing Images [1/3]")
        self.image_parser.parsing_pptx()
        self.image_parser.parsing_pdf()
        li = Path.iterdir(Path(File.Input))
        await self.generate_images(li)
        await self.move_images()
        await del_dir(File.Backup)
        shutil.move(f"{File.Input}", f"{File.Backup}")

        await asyncio.gather(
            *(del_dir(p) for p in [File.Input, ImageParser.Pptx, ImageParser.Pdfs])
        )

    async def parse_portfolio(self) -> None:
        print("Parsing Tagged Images [1/3]")
        li: Generator[Path, None, None] = Path.iterdir(Path(File.Portfolio))
        await self.generate_images(li)
        await self.move_images()
        await del_dir(File.Backup)
        shutil.move(f"{File.Portfolio}", f"{File.Backup}")
        await del_dir(File.Portfolio)

    async def parse_reference(self) -> None:
        print("Parsing Tagged Images [1/3]")
        li: Generator[Path, None, None] = Path.iterdir(Path(File.Reference))
        await self.generate_images(li)
        await self.move_images()
        await del_dir(File.Backup)
        shutil.move(f"{File.Reference}", f"{File.Backup}")
        await del_dir(File.Reference)

    def parsing_text(self):
        from src.net.mongo import Mongo
        from src.variables import Collections

        data = self.text_parser.get_dict()
        collections = [
            Collections.Engineering,
            Collections.Gallery,
            Collections.Medical,
            Collections.Logistics,
        ]

        def get_index(key: str):
            for i, coll in enumerate(collections):
                if coll.value == key:
                    return i
            return -1

        cli = Mongo(self.util)
        cli.conn()

        temp: dict[str, list[dict[str, Any]]] = {}

        for k in data.keys():
            if get_index(k) != -1:
                c = collections[get_index(k)]
                for title, url, time in data[k]:
                    y, m, d = [int(v) for v in time.split('-')]
                    if c.value not in temp:
                        temp[c.value] = []
                    temp[c.value].append({
                        "type": "link",
                        "title": title,
                        "url": url,
                        "when": datetime(y, m, d),
                    })

        for k, v in temp.items():
            if get_index(k) != -1:
                c = collections[get_index(k)]
                cli.insert_many_links(c, v)
