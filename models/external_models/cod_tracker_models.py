from dataclasses import dataclass
from typing import List


@dataclass
class WarzoneMatchMetadata:
    mode_name: str
    start_time_ts: int
    player_count: int
    team_count: int
    match_id: str


@dataclass
class WarzonePlayerStats:
    damage_done: int = 0
    deaths: int = 0
    gulag_deaths: int = 0
    gulag_kills: int = 0
    kills: int = 0
    team_placement: int = None
    time_played_sec: int = 0


@dataclass
class WarzonePlayerData:
    gamertag: str
    stats: WarzonePlayerStats


@dataclass
class WarzoneMatch:
    metadata: WarzoneMatchMetadata
    players: List[WarzonePlayerData]


@dataclass
class WarzonePlayerSearchResult:
    full_activision_username: str


@dataclass
class WarzonePlayerSearchResults:
    players: List[WarzonePlayerSearchResult]
