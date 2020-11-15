from dataclasses import dataclass
from typing import Dict, Any, List

import inflection
from marshmallow import fields, pre_load

from base_schema import AutobuildSchema
from models.external_models.cod_tracker_models import WarzoneMatchMetadata, WarzonePlayerStats, WarzonePlayerData, \
    WarzoneMatch

ALLIES_TEAM = 'allies'


class WarzoneMatchMetadataSchema(AutobuildSchema):

    _class_to_load = WarzoneMatchMetadata

    mode_name = fields.Str(data_key='modeName')
    start_time_ts = fields.Int(data_key='timestamp')
    player_count = fields.Int(data_key='playerCount')
    team_count = fields.Int(data_key='teamCount')
    match_id = fields.Str()


class WarzonePlayerStatsSchema(AutobuildSchema):
    _class_to_load = WarzonePlayerStats

    damage_done = fields.Int()
    deaths = fields.Int()
    gulag_deaths = fields.Int()
    gulag_kills = fields.Int()
    kills = fields.Int()
    team_placement = fields.Int()
    time_played_sec = fields.Int(data_key='time_played')


class WarzonePlayerDataSchema(AutobuildSchema):
    _class_to_load = WarzonePlayerData

    gamertag = fields.Str()
    stats = fields.Nested(WarzonePlayerStatsSchema)


class WarzoneMatchSchema(AutobuildSchema):
    _class_to_load = WarzoneMatch

    metadata = fields.Nested(WarzoneMatchMetadataSchema)
    players = fields.List(fields.Nested(WarzonePlayerDataSchema), data_key='segments')

    def _move_nested_fields_from_stat_dictionaries(self, player: Dict[str, Any]) -> None:
        fields_to_move = ['kills', 'gulagKills', 'gulagDeaths', 'damageDone', 'deaths', 'timePlayed', 'teamPlacement']
        for field in fields_to_move:
            # Turn camelCase to snake_case
            new_field_name = inflection.underscore(field)
            try:
                nested_value = player['stats'][field]['value']
            except KeyError as ke:
                print(f"Caught KeyError reading {field} from stat dictionary")
                nested_value = 0

            player['stats'][new_field_name] = nested_value

    def _move_nested_fields_to_root_level(self, data: Dict[str, Any]) -> None:
        try:
            # Move 'match_id' from the attributes dictionary to the metadata dictionary
            match_id = data['attributes']['id']
            data['metadata']['match_id'] = match_id
        except KeyError:
            print(f"Caught KeyError moving match_id {data}")

        for player in data['segments']:
            # The gamer tag is nested within the metadata dictionary. Move it up to the 'segment' level
            try:
                gamertag = player['metadata']['platformUserHandle']
                player['gamertag'] = gamertag
            except KeyError:
                print(f"Caught KeyError moving gamertag {player}")

            self._move_nested_fields_from_stat_dictionaries(player)

    def _delete_non_allied_players(self, data: Dict[str, Any]):
        allied_players_only = []
        for player in data['segments']:
            try:
                team_name = player['attributes']['team']
                if team_name == ALLIES_TEAM:
                    allied_players_only.append(player)
            except KeyError:
                pass

        data['segments'] = allied_players_only

    @pre_load
    def pre_load(self, data, **kwargs):
        self._move_nested_fields_to_root_level(data)
        return data


WARZONE_MATCH_SCHEMA = WarzoneMatchSchema()