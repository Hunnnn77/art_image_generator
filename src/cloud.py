from pathlib import Path
from datetime import datetime

from dotenv import dotenv_values
from src.time_tz import Util
import cloudinary
import cloudinary.uploader
import asyncio
import os.path
import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class Cloud:
    Last_Index = 0

    def __init__(self, util: Util) -> None:
        print("Uploading...")
        self.util = util

    @staticmethod
    def get_lastest_folder_path() -> str:
        paths = os.listdir(f"{os.getcwd()}/output")
        temp: datetime | None = None
        for i, p in enumerate(paths):
            date, time = p.split("_")
            time = time.replace("-", ":")
            y, m, d = [int(v) for v in date.split("-")]
            h, mi, sec = [int(v) for v in time.split(":")]
            if i == 0:
                temp = datetime(year=y, month=m, day=d, hour=h, minute=mi, second=sec)
            else:
                new_one = datetime(
                    year=y, month=m, day=d, hour=h, minute=mi, second=sec
                )
                if temp is not None:
                    if temp < new_one:
                        Cloud.Last_Index = i
        return paths[Cloud.Last_Index]

    def get_config(self, file: str) -> Path:
        return Path(f"{os.getcwd()}/src/_secret/{file}")

    async def update_to_cloudinary(
        self,
    ) -> tuple[tuple[list[str], list[str], list[str], list[str]], str]:
        config = dotenv_values(".env")
        cloudinary.config(
            cloud_name=config["CLOUD_NAME"],
            api_key=config["API_KEY"],
            api_secret=config["API_SECRET"],
            secure=True,
        )

        last_folder = self.get_lastest_folder_path()
        root_path = f"{os.getcwd()}/output/{last_folder}"
        original_full = f"{root_path}/original"
        resized_full = f"{root_path}/resized"
        resized_PL_full = f"{root_path}/resizedPL"

        resized = []
        resized_pl = []
        origin = []
        desc = []

        async def upload_images(paths: list[str]):
            for p in paths:
                if "_RESIZED" in p:
                    idx = p.rfind("_RESIZED")
                    r_300 = cloudinary.uploader.upload(
                        f"{resized_full}/{p}",
                        folder=f"{last_folder}/300px",
                        public_id=f"{p[:idx]}_300px",
                    )
                    resized.append(r_300["url"])
                elif "_PL" in p:
                    idx = p.rfind("_PL")
                    pl = cloudinary.uploader.upload(
                        f"{resized_PL_full}/{p}",
                        folder=f"{last_folder}/60px",
                        public_id=f"{p[:idx]}_60px",
                    )
                    resized_pl.append(pl["url"])
                else:
                    ori = cloudinary.uploader.upload(
                        f"{original_full}/{p}",
                        folder=f"{last_folder}/full",
                        public_id=f"{p}",
                    )
                    origin.append(ori["url"])
                    desc.append(ori["original_filename"])

        async with asyncio.TaskGroup() as tg:
            tg.create_task(upload_images(os.listdir(f"{original_full}")))
            tg.create_task(upload_images(os.listdir(f"{resized_full}")))
            tg.create_task(upload_images(os.listdir(f"{resized_PL_full}")))

        comb: tuple[list[str], list[str], list[str], list[str]] = (
            desc,
            origin,
            resized,
            resized_pl,
        )
        pprint.pp(comb)
        return comb, last_folder

    def get_auth(self):
        SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

        return creds

    def make_new_sheet(self, title: str, service, spreadsheet_id):
        body = {"requests": [{"addSheet": {"properties": {"title": title}}}]}
        try:
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body
            ).execute()
        except Exception as e:
            print(f"An error occurred: {e}")

    def share_to_cloud(
        self, pair: tuple[tuple[list[str], list[str], list[str], list[str]], str]
    ):
        config = dotenv_values(".env")
        id = config["ID"]
        creds = self.get_auth()

        try:
            li, title = pair
            service = build("sheets", "v4", credentials=creds)
            range_to_append = f"{title}!A1:Z"

            self.make_new_sheet(title, service, id)

            print(f"Row:{len(li[0])} / Col:{len(li)}")

            body = {
                "values": list(zip(li[1], li[2], li[3], li[0])),
            }

            response = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=id,
                    range=range_to_append,
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )
            pprint.pp(response)

        except HttpError as err:
            print(err)

    async def main(self):
        pair = await self.update_to_cloudinary()
        self.share_to_cloud(pair)
