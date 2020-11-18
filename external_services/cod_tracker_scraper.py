import urllib.parse
from typing import Tuple, List, Optional

import requests
from bs4 import BeautifulSoup
from marshmallow import ValidationError

from constants import MAX_CALLS, CORE_MODES
from models.player import Player
from schemas.warzone_match_schema import WarzoneMatch, WARZONE_MATCH_SCHEMA

PLAYER_MATCH_DATA_URL = "https://api.tracker.gg/api/v1/warzone/matches/atvi/{}?type=wz&next={}"
MATCH_DATA_URL = "https://api.tracker.gg/api/v1/warzone/matches/{}"
PLAYER_OVERVIEW_URL = "https://cod.tracker.gg/warzone/profile/atvi/{}?overview"
PLAYER_SEARCH_URL = "https://api.tracker.gg/api/v2/warzone/standard/search?platform=atvi&query={}&autocomplete=true"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}


class CodTrackerScraper:
    def get_all_new_match_ids_for_player(self, player: Player, last_match_recorded: Optional[str]) -> List[str]:
        """
        Fetches all matches a player has played up to a given end match or the 100 most recent (whichever is smaller)
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

    def _get_match_ids_for_player(self, player: Player, page_start: Optional[str]) -> Tuple[List[str], Optional[str]]:
        """
        Returns the next recent 20 match_ids for a player given a pagination start token
        If no token is provided, it will begin at the most recent match
        :param player:
        :param page_start:
        :return:
        """
        pagination_token = page_start if page_start else "null"
        url = PLAYER_MATCH_DATA_URL.format(player.get_urlencoded_activision_username(), pagination_token)
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

    def get_activision_id_for_gamertag(self, gamertag: str) -> Optional[str]:
        print(f"Getting Activision ID for {gamertag}")
        url_encoded_tag = urllib.parse.quote(gamertag)
        url = PLAYER_SEARCH_URL.format(url_encoded_tag)
        try:
            resp = requests.get(url, headers=HEADERS)
            resp.raise_for_status()
        except Exception as e:
            print(f"Getting Activision ID for {gamertag} failed {str(e)}")
            return None

        resp_data = resp.json()["data"]
        if len(resp_data) == 1:
            search_result = resp_data[0]
            full_username = search_result["platformUserIdentifier"]
            return full_username[len(gamertag) + 1 :]

        possible_options = []
        for search_result in resp_data:
            full_username = search_result["platformUserIdentifier"]
            # If the starting n (where n is the len of the tag) characters match w/o case sensitivity, its an option
            if gamertag.lower() == full_username[: len(gamertag)].lower():
                possible_options.append(full_username)

        for needle in [gamertag, gamertag.lower()]:
            for possible_option in possible_options:
                if gamertag == possible_option[: len(needle)]:
                    if len(possible_option) == len(needle):
                        # There is no Activision ID for some reason e.g "Yoda"
                        return ""
                    if "#" == possible_option[len(needle)]:
                        # Check if a '#' exists immediately after the tag
                        # There is an Activision ID and its a case sensitive match e.g "Yoda#548485"
                        return possible_option[len(needle) + 1 :]

        return None

        # Try matching with case sensitivity, if nothing matches, then go to all lowercase
        for needle in [gamertag, gamertag.lower()]:
            for search_result in resp_data:
                full_username = search_result["platformUserIdentifier"]
                if "#" not in full_username:
                    continue
                if needle != full_username[: len(needle)]:
                    continue
                if "#" != full_username[len(needle)]:
                    continue
                return full_username[len(needle) + 1 :]
            return None

    def get_last_7d_kd_ratio_for_player(self, player: Player) -> Optional[float]:
        print(f"Getting last 7d KD for {player.display_name}")
        url = PLAYER_OVERVIEW_URL.format(player.get_urlencoded_activision_username())
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        l7d_tag = soup.body.find(text="Last 7 Days")
        if not l7d_tag:
            return None
        last_7d_games_played = l7d_tag.parent.parent
        all_numbers = last_7d_games_played.find_all("div", class_="numbers")
        try:
            kd = float(
                next(
                    n.find("span", class_="value").text
                    for n in all_numbers
                    if n.find("span", class_="name").text == "K/D Ratio"
                )
            )
            print(f"L7D K/D for {player.display_name} is {kd}")
            return kd
        except StopIteration:
            return None

    def _filter_out_non_allied_players(self, player: Player, warzone_match_data: WarzoneMatch) -> WarzoneMatch:
        wz_player_data = next(p for p in warzone_match_data.players if p.gamertag == player.display_name)
        final_position = wz_player_data.stats.team_placement
        allied_players = [p for p in warzone_match_data.players if p.stats.team_placement == final_position]
        warzone_match_data.players = allied_players
        return warzone_match_data

    def _get_match_data(self, match_id: str, player: Optional[Player] = None) -> Optional[WarzoneMatch]:
        url = MATCH_DATA_URL.format(match_id)
        params = {"handle": player.get_urlencoded_display_name()} if player else {}
        try:
            resp = requests.get(url, headers=HEADERS, params=params)
            resp.raise_for_status()
        except Exception as e:
            print(f"Fetching data for match {match_id} failed with {str(e)}")
            return None

        try:
            return WARZONE_MATCH_SCHEMA.load(resp.json()["data"])
        except ValidationError as ve:
            print(f"Fetching data for {match_id} failed with a Marshmallow error {str(ve)}")
            return None

    def get_all_data_for_match(self, match_id: str) -> WarzoneMatch:
        print(f"Fetching enemy data for match {match_id}")
        match_data = self._get_match_data(match_id)
        if not match_data:
            return None
        return match_data

    def get_team_data_for_match(self, match_id: str, player: Player) -> Optional[WarzoneMatch]:
        print(f"Fetching data for match {match_id}")
        warzone_match_data = self._get_match_data(match_id, player)
        if not warzone_match_data:
            return None
        if warzone_match_data.metadata.mode_name not in CORE_MODES:
            return None
        return self._filter_out_non_allied_players(player, warzone_match_data)
