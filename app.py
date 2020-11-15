from typing import List
from datetime import datetime

from constants import MAHITH, TIME_FORMAT, TEAM_ROW_FORMAT, INDIVIDUAL_PLAYER_ROW_FORMAT, GAMERTAG_TO_NAME_MAP
from services.cod_tracker_scraper import CodTrackerScraper
from time import time

from services.google_sheets_api import GoogleSheetsApi


class WarzoneData:
    def __init__(self):
        self.scraper = CodTrackerScraper()
        self.google_sheets_api = GoogleSheetsApi()

    def write_warzone_stats_to_google_sheets(self, match_ids: List[str]):
        indiv_rows_to_be_written = []
        team_rows_to_be_written = []
        for match_id in match_ids[::-1]:
            warzone_match_data = self.scraper.get_data_for_match(match_id, MAHITH)
            if not warzone_match_data:
                continue
            warzone_player = next(
                player for player in warzone_match_data.players if player.gamertag == MAHITH.display_name
            )
            utc_dt = datetime.utcfromtimestamp(warzone_match_data.metadata.start_time_ts)
            formatted_time = utc_dt.strftime(TIME_FORMAT)
            players = [GAMERTAG_TO_NAME_MAP.get(p.gamertag, "Random") for p in warzone_match_data.players]
            deduped_players = list(set(players))
            deduped_players.sort()
            roster_str = ",".jon(deduped_players)
            row_as_str = INDIVIDUAL_PLAYER_ROW_FORMAT.format(
                match_id=match_id,
                time=formatted_time,
                placement=warzone_player.stats.team_placement,
                kills=warzone_player.stats.kills,
                deaths=warzone_player.stats.deaths,
                gulag_kills=warzone_player.stats.gulag_kills,
                dmg_done=warzone_player.stats.damage_done,
                gulag_deaths=warzone_player.stats.gulag_deaths,
                roster=roster_str,
            )
            team_kills = sum(p.stats.kills for p in warzone_match_data.players)
            team_deaths = sum(p.stats.deaths for p in warzone_match_data.players)
            combined_dmg = sum(p.stats.damage_done for p in warzone_match_data.players)
            game_length = max(p.stats.time_played_sec for p in warzone_match_data.players)
            team_placement = next(p.stats.team_placement for p in warzone_match_data.players)
            players = [GAMERTAG_TO_NAME_MAP.get(p.gamertag, "Random") for p in warzone_match_data.players]
            deduped_players = list(set(players))
            deduped_players.sort()
            roster_str = ",".jon(deduped_players)
            row = row_as_str.split(",")
            print(row)
            indiv_rows_to_be_written.append(row)
            team_row_as_str = TEAM_ROW_FORMAT.format(
                match_id=match_id,
                time=formatted_time,
                game_duration=game_length,
                placement=team_placement,
                kills=team_kills,
                deaths=team_deaths,
                dmg_done=combined_dmg,
                roster=roster_str,
            )

            team_row = team_row_as_str.split(",")
            team_rows_to_be_written.append(team_row)

        self.google_sheets_api.write_new_game_data_for_player(MAHITH, indiv_rows_to_be_written)

    def run(self):
        start_time = time()
        latest_match_recorded = self.google_sheets_api.get_last_match_recorded(MAHITH)
        match_ids = self.scraper.get_all_new_match_ids_for_player(MAHITH, latest_match_recorded)
        self.write_warzone_stats_to_google_sheets(match_ids)
        end_time = time()
        print(f"Run took {end_time-start_time} seconds")


if __name__ == "__main__":
    wz_data = WarzoneData()
    wz_data.run()
