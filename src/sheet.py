import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path


class Sheet:
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    SAMPLE_SPREADSHEET_ID = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
    SAMPLE_RANGE_NAME = "Class Data!A2:E"

    @classmethod
    def get_file(cls, file: str) -> Path:
        return Path(f"{os.getcwd()}/src/_secret/{file}")

    def main(self):
        creds = None

        json_path = Sheet.get_file("token.json")
        cred_path = Sheet.get_file("cred.json")

        if json_path.exists():
            creds = Credentials.from_authorized_user_file(json_path, Sheet.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cred_path, Sheet.SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(json_path, "w") as token:
                token.write(creds.to_json())

        try:
            service = build("sheets", "v4", credentials=creds)

            sheet = service.spreadsheets()
            result = (
                sheet.values()
                .get(
                    spreadsheetId=Sheet.SAMPLE_SPREADSHEET_ID,
                    range=Sheet.SAMPLE_RANGE_NAME,
                )
                .execute()
            )
            values = result.get("values", [])

            if not values:
                print("No data found.")
                return

            print("Name, Major:")
            for row in values:
                print(f"{row[0]}, {row[4]}")
        except HttpError as err:
            print(err)
