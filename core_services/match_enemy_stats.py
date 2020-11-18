from time import sleep
from typing import List, Tuple

from external_services.cod_tracker_scraper import CodTrackerScraper
from models.player import Player


class MatchEnemyStats:
    def __init__(self):
        self.scraper = CodTrackerScraper()
        self.total_players_in_match = 0
        self.skipped_players = 0

    def display_stats_for_enemies_in_match(self, match_id: str) -> None:
        team_avg_kd, all_player_kd = self.pull_stats_for_enemies_in_match(match_id)
        if not team_avg_kd or not all_player_kd:
            return
        min_kd_in_match = min(all_player_kd)
        max_kd_in_match = max(all_player_kd)
        avg_kd_in_match = round(sum(all_player_kd) / len(all_player_kd), 2)
        avg_kd_of_teams = round(sum(team_avg_kd) / len(team_avg_kd), 2)
        kd_top_15 = team_avg_kd[:15]

        print(
            f"""
Match {match_id} Player Stats
There is data for {self.total_players_in_match - self.skipped_players}/{self.total_players_in_match}
The average K/D for all players is {avg_kd_in_match}
The best K/D is {max_kd_in_match}
The lowest K/D is {min_kd_in_match}

There is data for {len(team_avg_kd)} teams
The average K/D of all teams is {avg_kd_of_teams}
              """
        )
        for idx, top_15_team in enumerate(kd_top_15):
            print(f"Team #{idx + 1}'s K/D is {top_15_team}")

    def pull_stats_for_enemies_in_match(self, match_id: str) -> Tuple[List[float], List[float]]:
        warzone_match_data = self.scraper.get_all_data_for_match(match_id)
        if not warzone_match_data:
            return [], []
        team_array = [[] for i in range(warzone_match_data.metadata.team_count)]
        team_avg_kd = []
        all_player_kds = []
        for wz_player in warzone_match_data.players:
            sleep(3)
            self.total_players_in_match += 1
            activision_id = self.scraper.get_activision_id_for_gamertag(wz_player.gamertag)
            if activision_id is None:
                self.skipped_players += 1
                continue
            player = Player(activision_id=activision_id, display_name=wz_player.gamertag, name="")
            player_kd = self.scraper.get_last_7d_kd_ratio_for_player(player)
            if not player_kd:
                self.skipped_players += 1
                continue
            all_player_kds.append(player_kd)
            team_array[wz_player.stats.team_placement - 1].append(player_kd)

        for team in team_array:
            if not team:
                continue
            average_kd_of_team = round(sum(team) / len(team), 2)
            team_avg_kd.append(average_kd_of_team)

        return team_avg_kd, all_player_kds
