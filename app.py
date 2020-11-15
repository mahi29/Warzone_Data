from typing import List, Dict
from datetime import datetime

from constants import (
    TIME_FORMAT,
    TEAM_ROW_FORMAT,
    INDIVIDUAL_PLAYER_ROW_FORMAT,
    GAMERTAG_TO_NAME_MAP,
    TEAM_ROSTERS,
    TEAM_R306,
    TEAM_MBDF,
)
from models.external_models.cod_tracker_models import WarzoneMatch, WarzonePlayerData
from models.player import Player
from services.cod_tracker_scraper import CodTrackerScraper
from time import time

from services.google_sheets_api import GoogleSheetsApi


class WarzoneData:
    def __init__(self):
        self.scraper = CodTrackerScraper()
        self.google_sheets_api = GoogleSheetsApi()
        self.warzone_match_cache: Dict[str, WarzoneMatch] = {}

    def _get_team_roster_for_match(self, warzone_match_data: WarzoneMatch) -> List[str]:
        players = [GAMERTAG_TO_NAME_MAP.get(p.gamertag, "Random") for p in warzone_match_data.players]
        deduped_players = list(set(players))
        deduped_players.sort()
        return deduped_players

    def _get_data_for_team_row(self, warzone_match_data: WarzoneMatch) -> List[str]:
        utc_dt = datetime.utcfromtimestamp(warzone_match_data.metadata.start_time_ts)
        formatted_time = utc_dt.strftime(TIME_FORMAT)
        team_kills = sum(p.stats.kills for p in warzone_match_data.players)
        team_deaths = sum(p.stats.deaths for p in warzone_match_data.players)
        combined_dmg = sum(p.stats.damage_done for p in warzone_match_data.players)
        game_length = max(p.stats.time_played_sec for p in warzone_match_data.players)
        team_placement = next(p.stats.team_placement for p in warzone_match_data.players)
        team_roster = self._get_team_roster_for_match(warzone_match_data)
        team_row_as_str = TEAM_ROW_FORMAT.format(
            match_id=warzone_match_data.metadata.match_id,
            time=formatted_time,
            game_duration=game_length,
            placement=team_placement,
            kills=team_kills,
            deaths=team_deaths,
            dmg_done=combined_dmg,
            roster="|".join(team_roster),
            mode=warzone_match_data.metadata.mode_name,
            win=1 if team_placement == 1 else 0,
            top_five=1 if team_placement <= 5 else 0,
        )

        return team_row_as_str.split(",")

    def _get_data_for_individual_row(
        self, warzone_player: WarzonePlayerData, warzone_match_data: WarzoneMatch
    ) -> List[str]:
        utc_dt = datetime.utcfromtimestamp(warzone_match_data.metadata.start_time_ts)
        formatted_time = utc_dt.strftime(TIME_FORMAT)
        team_roster = self._get_team_roster_for_match(warzone_match_data)
        row_as_str = INDIVIDUAL_PLAYER_ROW_FORMAT.format(
            match_id=warzone_match_data.metadata.match_id,
            time=formatted_time,
            placement=warzone_player.stats.team_placement,
            kills=warzone_player.stats.kills,
            deaths=warzone_player.stats.deaths,
            gulag_kills=warzone_player.stats.gulag_kills,
            dmg_done=warzone_player.stats.damage_done,
            gulag_deaths=warzone_player.stats.gulag_deaths,
            roster="|".join(team_roster),
            mode=warzone_match_data.metadata.mode_name,
        )
        return row_as_str.split(",")

    def write_team_stats_to_google_sheets(self, team: str):
        all_teammates = set(p.name for p in TEAM_ROSTERS[team])
        all_matches_played_by_all_teammates = list(self.warzone_match_cache.values())
        all_matches_played_by_all_teammates.sort(key=lambda wz_match: wz_match.metadata.start_time_ts)
        team_data = []
        for match in all_matches_played_by_all_teammates:
            team_roster = self._get_team_roster_for_match(match)
            if len(set(team_roster) & all_teammates) < 2:
                # If you haven't played with any of your other teammates, don't include it in the team charts
                continue
            row = self._get_data_for_team_row(match)
            team_data.append(row)
        self.google_sheets_api.write_new_game_data_for_team(team, team_data)

    def write_warzone_individual_stats_to_google_sheets(self, player: Player, team: str, match_ids: List[str]):
        indiv_rows_to_be_written = []
        for match_id in match_ids[::-1]:
            if match_id not in self.warzone_match_cache:
                match_data = self.scraper.get_data_for_match(match_id, player)
                if not match_data:
                    continue
                self.warzone_match_cache[match_id] = match_data
            warzone_match_data = self.warzone_match_cache[match_id]

            warzone_player = next(p for p in warzone_match_data.players if p.gamertag == player.display_name)
            row = self._get_data_for_individual_row(
                warzone_player=warzone_player, warzone_match_data=warzone_match_data
            )
            print(row)
            indiv_rows_to_be_written.append(row)

        self.google_sheets_api.write_new_game_data_for_player(player, team, indiv_rows_to_be_written)

    def run_for_team(self, team: str) -> None:
        total_roster = TEAM_ROSTERS[team]
        for player in total_roster:
            print(f"\nPulling stats for {player.name}")
            latest_match_recorded = self.google_sheets_api.get_last_match_recorded(player, team)
            match_ids = self.scraper.get_all_new_match_ids_for_player(player, latest_match_recorded)
            self.write_warzone_individual_stats_to_google_sheets(player, team, match_ids)
        self.write_team_stats_to_google_sheets(team)

    def prompt_user_for_team(self):
        try:
            team_choice_input = int(input("Select a team to pull stats for\n1: Room306\n2: MBDF\n"))
        except ValueError:
            raise Exception("Please pick one of the valid options")

        if team_choice_input not in [1, 2]:
            raise Exception("Please pick one of the valid options")

        team = TEAM_R306 if team_choice_input == 1 else TEAM_MBDF
        print(f"\nAggregating results for {team}...\n")
        return team

    def run(self):
        start_time = time()
        team = self.prompt_user_for_team()
        self.run_for_team(team)
        end_time = time()
        print(f"Run took {end_time-start_time} seconds")


if __name__ == "__main__":
    wz_data = WarzoneData()
    wz_data.run()
