import asyncio
import os
import shutil
from pathlib import Path
from typing import Generator

from src.image_parser import ImageGenerator, ImageParser
from src.text_parser import TextParser
from src.util import CWD, Util


class File:
    Input = f"{CWD}/input"
    Secret = f"{CWD}/@secret"
    Backup = f"{CWD}/_backup"
    Output = f"{CWD}/_output"
    Origin = f"{Output}/original"
    Resized = f"{Output}/resized"
    ResizedPL = f"{Output}/resizedPL"

    def __init__(self, util: Util) -> None:
        self.util = util
        self.image = ImageGenerator()
        self.image_parser = ImageParser()
        self.text_parser = TextParser()

    def _make_dir(self, path: str):
        p = Path(path)
        if not p.exists():
            p.mkdir()

    async def _delete_dir(self, dir: str):
        shutil.rmtree(dir, ignore_errors=True)
        if not Path(dir).exists():
            Path(dir).mkdir()

    def init(self):
        for v in [
            File.Secret,
            File.Input,
            File.Output,
            ImageParser.Pptx,
            ImageParser.Pdfs,
            File.Origin,
            File.Resized,
            File.ResizedPL,
            File.Backup,
        ]:
            self._make_dir(v)

    async def generate_images(
        self, li: Generator[Path, None, None], folder_name: str = ""
    ):
        resized = ""
        pl = ""

        for i, path in enumerate(li):
            if path.is_file():
                img, size = self.image.get_image_with_size(f"{path.absolute()}")

                if "." not in path.stem:
                    resized = (
                        path.name.split(".")[0].replace(" ", "")
                        + "_RESIZED"
                        + path.suffix
                    )
                    pl = path.name.split(".")[0].replace(" ", "") + "_PL" + path.suffix
                else:
                    resized: str = (
                        path.stem.replace(".", "_").replace(" ", "")
                        + "_RESIZED"
                        + path.suffix
                    )
                    pl: str = (
                        path.stem.replace(".", "_").replace(" ", "")
                        + "_PL"
                        + path.suffix
                    )

                if len(resized) == 0:
                    raise Exception("fileN isn't captured")

                await asyncio.gather(
                    self.image.save_image(
                        image=img,
                        location=File.Origin,
                        fileName=path.name.replace(" ", "")
                        if not folder_name
                        else folder_name + "_" + path.name.replace(" ", ""),
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

            await asyncio.gather(*(self._delete_dir(p) for p in paths))

        async def moving(dir: str):
            shutil.move(dir, dest)

        await asyncio.gather(
            *(moving(p) for p in [File.Origin, File.Resized, File.ResizedPL])
        )

    async def main(self):
        self.init()

        if len(os.listdir(f"{os.getcwd()}/input")) == 0:
            raise Exception("Empty Inputs!")

        print("Parsing Images [1/3]")
        self.image_parser.parsing_pptx()
        self.image_parser.parsing_pdf()
        li = Path.iterdir(Path(File.Input))
        await self.generate_images(li)
        await self.move_images()
        await self._delete_dir(File.Backup)
        shutil.move(f"{File.Input}", f"{File.Backup}")

        await asyncio.gather(
            *(
                self._delete_dir(p)
                for p in [File.Input, ImageParser.Pptx, ImageParser.Pdfs]
            )
        )
