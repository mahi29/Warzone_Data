from constants import (
    TEAM_R306,
    TEAM_MBDF,
    RunOptions,
)
from core_services.match_enemy_stats import MatchEnemyStats
from core_services.team_data_aggregator import TeamDataAggregator
from time import time


class WarzoneData:
    def __init__(self):
        self.team_data_aggregator = TeamDataAggregator()
        self.match_enemy_stats = MatchEnemyStats()

    def prompt_user_for_run_type(self):
        try:
            run_choice_input = int(
                input(
                    "What would you like to do?\n1: Fetch and upload team stats\n2: Pull stats about enemies in a match\n"
                )
            )
            return RunOptions(run_choice_input)
        except ValueError:
            raise Exception("Please pick one of the valid options")

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

    def prompt_user_for_match_id(self):
        match_id_input = input("Enter the match_id to pull enemy stats for\n")
        if not match_id_input.isdigit():
            raise Exception("The match ID should be only numbers")

        return match_id_input

    def run(self):
        start_time = time()
        run_choice = self.prompt_user_for_run_type()
        if run_choice == RunOptions.TEAM_STATS:
            team = self.prompt_user_for_team()
            self.team_data_aggregator.run_for_team(team)
        else:
            match_id = self.prompt_user_for_match_id()
            self.match_enemy_stats.display_stats_for_enemies_in_match(match_id)
        end_time = time()
        print(f"Run took {end_time-start_time} seconds")


if __name__ == "__main__":
    wz_data = WarzoneData()
    wz_data.run()
