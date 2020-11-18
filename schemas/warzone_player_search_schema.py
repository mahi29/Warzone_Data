from marshmallow import fields

from models.external_models.cod_tracker_models import WarzonePlayerSearchResults, WarzonePlayerSearchResult
from schemas.base_schema import AutobuildSchema


class WarzonePlayerSearchResultSchema(AutobuildSchema):
    _class_to_load = WarzonePlayerSearchResult

    full_activision_username = fields.Str(data_key="platformUserIdentifier")


class WarzonePlayersSearchResultsSchema(AutobuildSchema):
    _class_to_load = WarzonePlayerSearchResults

    players = fields.List(fields.Nested(WarzonePlayerSearchResultSchema), data_key="segments")
    deaths = fields.Int()
    gulag_deaths = fields.Int()
    gulag_kills = fields.Int()
    kills = fields.Int()
    team_placement = fields.Int()
    time_played_sec = fields.Int(data_key="time_played")
