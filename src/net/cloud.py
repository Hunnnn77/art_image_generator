import asyncio
import json
import os.path
import pprint
from datetime import datetime
from pathlib import Path
from typing import Any

from src.parser.text import TextParser
from src.util import Util


def get_creds():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = None
    secret_path = f"{os.getcwd()}/@secret"

    try:
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file(
                f"{secret_path}/token.json", SCOPES
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    f"{secret_path}/credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)
                with open(f"{secret_path}/token.json", "w") as token:
                    token.write(creds.to_json())
    except Exception as e:
        print(f"An error occurred: {e}")

    return creds


class Cloud:
    Last_Index = 0

    def __init__(self, util: Util, sheet_id: str) -> None:
        self.util = util
        self.sheet_id = sheet_id

    @staticmethod
    def get_latest_folder_path() -> str:
        paths = os.listdir(f"{os.getcwd()}/_output")
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

    async def update_to_cloudinary(
            self, is_tagged: bool
    ) -> (
            tuple[tuple[list[str], list[str], list[str], list[str]], str]
            | tuple[tuple[list[str], list[str]], str]
    ):
        import cloudinary
        import cloudinary.uploader

        cloudinary.config(
            cloud_name=self.util.get_envs("CLOUD_NAME"),
            api_key=self.util.get_envs("API_KEY"),
            api_secret=self.util.get_envs("API_SECRET"),
            secure=True,
        )

        last_folder_name = self.get_latest_folder_path()
        root_path = f"{os.getcwd()}/_output/{last_folder_name}"
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
                        folder=f"{last_folder_name}/300px",
                        public_id=f"{p[:idx]}_300px",
                    )
                    resized.append(r_300["url"])
                elif "_PL" in p:
                    idx = p.rfind("_PL")
                    pl = cloudinary.uploader.upload(
                        f"{resized_PL_full}/{p}",
                        folder=f"{last_folder_name}/60px",
                        public_id=f"{p[:idx]}_60px",
                    )
                    resized_pl.append(pl["url"])
                else:
                    remove_ext = p.split(".")[0]
                    ori = cloudinary.uploader.upload(
                        f"{original_full}/{p}",
                        folder=f"{last_folder_name}/full",
                        public_id=f"{remove_ext}",
                    )
                    origin.append(ori["url"])
                    desc.append(ori["original_filename"])

        if not is_tagged:
            await asyncio.gather(
                *(
                    upload_images(os.listdir(p))
                    for p in [original_full, resized_full, resized_PL_full]
                )
            )
            comb = (
                desc,
                origin,
                resized,
                resized_pl,
            )
            pprint.pp(comb)
            return comb, last_folder_name
        else:
            await upload_images(os.listdir(original_full))
            comb = (
                desc,
                origin,
            )
            pprint.pp(comb)
            return comb, last_folder_name

    def new_sheet(self, service, spreadsheet_id):
        title = self.util.get_time_tz()
        body = {"requests": [{"addSheet": {"properties": {"title": title}}}]}
        try:
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body
            ).execute()
        except Exception as e:
            print(f"An error occurred: {e}")
        return title

    def update_sheet(
            self, pair: tuple[tuple[list[str], list[str], list[str], list[str]], str]
    ):
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError

        sheet_id = self.util.get_envs("ID") if self.sheet_id == "" else self.sheet_id
        creds = get_creds()

        try:
            li, _ = pair
            service = build("sheets", "v4", credentials=creds)
            title = self.new_sheet(service, sheet_id)
            range_to_append = f"{title}!A1:Z"

            names = [v.split("_")[0] for v in li[0]]
            titles = [v.split("_")[1] for v in li[0]]

            values = list(
                zip(li[1], li[2], li[3], names, titles)
            )  # [ [origin, 300, 60, name] ]

            print(f"w:{len(li)} / h:{len(li[0])}")
            body = {
                "values": values,
            }

            response = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=sheet_id,
                    range=range_to_append,
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )
            pprint.pp(response)

        except HttpError as err:
            print(err)

    def generating_json(self):
        from googleapiclient.discovery import build
        print("Generating json [1/1]")

        creds = get_creds()
        service = build("sheets", "v4", credentials=creds)
        id = self.util.get_envs("ID") if self.sheet_id == "" else self.sheet_id
        range_name = "seed!A1:Z"

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        data = []
        for _, P_300, _, name, title, materials, size, year in rows:
            data.append(
                {
                    "name": name,
                    "year": year,
                    "title": title.split("@")[0],
                    "materials": materials,
                    "size": size,
                    "img": P_300,
                }
            )
        json_string = json.dumps(data)
        save_path = Path(f"{os.getcwd()}/_json")
        if not save_path.exists():
            save_path.mkdir()
        with open(f"{save_path}/{self.util.get_time_tz()}.json", "w") as f:
            f.write(json_string)

    async def parse_original(self):
        print("Uploading [2/3]")
        pair = await self.update_to_cloudinary(False)
        print("Uploading [3/3]")
        assert len(pair[0]) == 4, "desc, original, resized, pl"
        self.update_sheet(pair)  # type: ignore

    async def parse_tagged(self):
        from src.net.mongo import Mongo
        from src.variables import Collections

        print("Uploading Tagged [2/3]")
        urls, _ = await self.update_to_cloudinary(True)
        assert len(urls) == 2, "desc, original"

        list_of = [{
            "type": "img",
            "title": f"{datetime.now().strftime("%B")} {datetime.now().year}",
            "url": url,
            "year": datetime.now().year
        } for url in urls[1]]

        print("Inserting Images to Database [3/3]")
        cli = Mongo(self.util)
        cli.conn()
        cli.insert_images(Collections.Gallery, list_of)

