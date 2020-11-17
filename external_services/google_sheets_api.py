import pickle
import os.path
from typing import Optional, List

from googleapiclient import discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from constants import TEAM_TO_SHEET_ID
from models.player import Player

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
RANGE = "A:Z"


class GoogleSheetsApi:
    def __init__(self):
        self.credentials = self.get_or_create_authorization()
        self.google_sheets_service = discovery.build("sheets", "v4", credentials=self.credentials)

    def get_or_create_authorization(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        return creds

    def _append_data_to_sheet(self, spreadsheet_id: str, sheet: str, data: List[List[str]]) -> None:
        body = {"values": data}
        request = (
            self.google_sheets_service.spreadsheets()
            .values()
            .append(spreadsheetId=spreadsheet_id, range=sheet, body=body, valueInputOption="USER_ENTERED")
        )
        result = request.execute()
        return result

    def write_new_game_data_for_team(self, team: str, match_data: List[List[str]]) -> None:
        return self._append_data_to_sheet(spreadsheet_id=TEAM_TO_SHEET_ID[team], sheet="Overall", data=match_data)

    def write_new_game_data_for_player(self, player: Player, team: str, match_data: List[List[str]]) -> None:
        return self._append_data_to_sheet(spreadsheet_id=TEAM_TO_SHEET_ID[team], sheet=player.name, data=match_data)

    def get_last_match_recorded(self, player: Player, team: str) -> Optional[str]:
        spreadsheet_id = TEAM_TO_SHEET_ID[team]
        request = (
            self.google_sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=player.name)
        )
        result = request.execute()
        values = result.get("values", [])
        if len(values) < 2:
            return None
        return values[-1][0]
