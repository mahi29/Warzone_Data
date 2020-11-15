from constants import MAHITH
from services.cod_tracker_scraper import CodTrackerScraper
from time import time


class WarzoneData:
    def __init__(self):
        self.scraper = CodTrackerScraper()

    def run(self):
        start_time = time()
        match_ids = self.scraper.get_all_new_match_ids_for_player(MAHITH, None)
        kills, deaths = 0, 0
        for match_id in match_ids:
            warzone_match_data = self.scraper.get_data_for_match(match_id, MAHITH)
            try:
                warzone_player = next(player for player in warzone_match_data.players if player.gamertag == MAHITH.display_name)
            except StopIteration:
                breakpoint()
            kills += warzone_player.stats.kills
            deaths += warzone_player.stats.deaths

        kd = round(kills/deaths, 2)
        end_time = time()
        print(f"Over the last {len(match_ids)} games, you have {kills} kills and {deaths} deaths for a K/D of {kd}")
        print(f"Run took {end_time-start_time} seconds")


if __name__ == '__main__':
    wz_data = WarzoneData()
    wz_data.run()