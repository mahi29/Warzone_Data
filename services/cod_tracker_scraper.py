from typing import Tuple, List, Optional

import requests

from constants import MAX_CALLS
from models.player import Player
from warzone_match_schema import WarzoneMatch, WARZONE_MATCH_SCHEMA

PLAYER_DATA_URL = "https://api.tracker.gg/api/v1/warzone/matches/atvi/{}?type=wz&next={}"
MATCH_DATA_URL = "https://api.tracker.gg/api/v1/warzone/matches/{}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}


class CodTrackerScraper:
    def get_all_new_match_ids_for_player(self, player: Player, last_match_recorded: str):
        """
        Fetches all the matches a player has played upto a given end match or the 100 most recent (whichever is smaller)
        :param player:
        :param last_match_recorded:
        :return:
        """
        pagination_token = None
        all_new_match_ids = []
        num_calls_so_far = 0
        while num_calls_so_far < MAX_CALLS:
            match_ids, pagination_token = self._get_match_ids_for_player(player, pagination_token)
            for match_id in match_ids:
                if match_id == last_match_recorded:
                    return all_new_match_ids
                all_new_match_ids.append(match_id)
            num_calls_so_far += 1

        return all_new_match_ids

    def _get_match_ids_for_player(self, player: Player, page_start: Optional[str]) -> Tuple[List[str], str]:
        """
        Returns the next recent 20 match_ids for a player given a pagination start token
        If no token is provided, it will begin at the most recent match
        :param player:
        :param page_start:
        :return:
        """
        pagination_token = page_start if page_start else "null"
        url = PLAYER_DATA_URL.format(player.get_urlencoded_activision_username(), pagination_token)
        match_ids = []
        try:
            resp = requests.get(url, headers=HEADERS)
            resp.raise_for_status()
        except Exception as e:
            print(f"Fetching data for {player.display_name} failed {str(e)}")
            return [], None

        resp_data = resp.json()["data"]
        matches_data = resp_data["matches"]
        for match_data in matches_data:
            match_id = match_data["attributes"]["id"]
            match_ids.append(match_id)
        return match_ids, resp_data["metadata"]["next"]

    def _filter_out_non_allied_players(self, player: Player, warzone_match_data: WarzoneMatch) -> WarzoneMatch:
        wz_player_data = next(p for p in warzone_match_data.players if p.gamertag == player.display_name)
        final_position = wz_player_data.stats.team_placement
        allied_players = [p for p in warzone_match_data.players if p.stats.team_placement == final_position]
        warzone_match_data.players = allied_players
        return warzone_match_data

    def get_data_for_match(self, match_id: int, player: Player) -> Optional[WarzoneMatch]:
        print(f"Fetching data for match {match_id}")
        url = MATCH_DATA_URL.format(match_id)
        params = {"handle": player.get_urlencoded_display_name()}
        try:
            resp = requests.get(url, headers=HEADERS, params=params)
            resp.raise_for_status()
        except Exception as e:
            print(f"Fetching data for match {match_id} failed with {str(e)}")
            return None

        warzone_match_data: WarzoneMatch = WARZONE_MATCH_SCHEMA.load(resp.json()["data"])
        return self._filter_out_non_allied_players(player, warzone_match_data)
