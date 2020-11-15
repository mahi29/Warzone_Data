from typing import List
from datetime import datetime

from constants import MAHITH, TIME_FORMAT
from services.cod_tracker_scraper import CodTrackerScraper
from time import time

from services.google_sheets_api import GoogleSheetsApi


class WarzoneData:
    def __init__(self):
        self.scraper = CodTrackerScraper()
        self.google_sheets_api = GoogleSheetsApi()

    def write_warzone_stats_to_google_sheets(self, match_ids: List[str]):
        rows_to_be_written = []
        row_format = "{match_id},{time},{placement},{kills},{deaths},{dmg_done},{gulag_kills},{gulag_deaths}"
        for match_id in match_ids[::-1]:
            warzone_match_data = self.scraper.get_data_for_match(match_id, MAHITH)
            if not warzone_match_data:
                continue
            warzone_player = next(
                player for player in warzone_match_data.players if player.gamertag == MAHITH.display_name
            )
            utc_dt = datetime.utcfromtimestamp(warzone_match_data.metadata.start_time_ts)
            formatted_time = utc_dt.strftime(TIME_FORMAT)
            row_as_str = row_format.format(
                match_id=match_id,
                time=formatted_time,
                placement=warzone_player.stats.team_placement,
                kills=warzone_player.stats.kills,
                deaths=warzone_player.stats.deaths,
                gulag_kills=warzone_player.stats.gulag_kills,
                dmg_done=warzone_player.stats.damage_done,
                gulag_deaths=warzone_player.stats.gulag_deaths,
            )
            row = row_as_str.split(",")
            print(row)
            rows_to_be_written.append(row)

        self.google_sheets_api.write_new_game_data_for_player(MAHITH, rows_to_be_written)

    def run(self):
        start_time = time()
        match_ids = self.scraper.get_all_new_match_ids_for_player(MAHITH, None)
        self.write_warzone_stats_to_google_sheets(match_ids)
        end_time = time()
        print(f"Run took {end_time-start_time} seconds")


if __name__ == "__main__":
    wz_data = WarzoneData()
    wz_data.run()
