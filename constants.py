from models.player import Player

MAX_CALLS = 5

BRIAN = Player(activision_id="8226586", name="Brian", display_name="Harmuny")
JUSTIN = Player(activision_id="2716959", name="Justin", display_name="jsquared8")
MAHITH = Player(activision_id="4702806", name="Mahith", display_name="x Pr1mal Fear x")
NOAH = Player(activision_id="5991323", name="Noah", display_name="nefron55")
PATRICK = Player(activision_id="1104000", name="Patrick", display_name="coysenberry")
RAVI = Player(activision_id="3102549", name="Ravi", display_name="rdykl")
VINNY = Player(activision_id="9821768", name="Vinny", display_name="TheCastleDaddy")

TIME_FORMAT = "%m/%d/%Y %H:%M"
INDIVIDUAL_PLAYER_ROW_FORMAT = (
    "{match_id},{time},{placement},{kills},{deaths},{dmg_done},{gulag_kills},{gulag_deaths},{roster},{mode}"
)
TEAM_ROW_FORMAT = "{match_id},{time},{game_duration},{placement},{kills},{deaths},{dmg_done},{roster},{mode}"


GAMERTAG_TO_NAME_MAP = {
    "Harmuny": "Brian",
    "jsquared8": "Justin",
    "x Pr1mal Fear x": "Mahith",
    "nefron55": "Noah",
    "coysenberry": "Patrick",
    "rdykl": "Ravi",
    "TheCastleDaddy": "Vinny",
}

NAME_TO_PLAYER_MAP = {
    "Brian": BRIAN,
    "Justin": JUSTIN,
    "Mahith": MAHITH,
    "Noah": NOAH,
    "Patrick": PATRICK,
    "Ravi": RAVI,
    "Vinny": VINNY,
}

TEAM_R306 = "R306"
TEAM_MBDF = "MBDF"

TEAM_ROSTERS = {TEAM_R306: [MAHITH, NOAH, PATRICK, RAVI], TEAM_MBDF: [BRIAN, JUSTIN, MAHITH, VINNY]}

MBDF_SHEET_ID = "1wafgNIgMskQh9_UI0yyXppsoaSJhRottbK0iV8thIXQ"
R306_SHEET_ID = "1RI8-POdqf2UHHa2B86EW7-krQ0ED9hiFu5yXBN4GacE"

TEAM_TO_SHEET_ID = {
    TEAM_R306: R306_SHEET_ID,
    TEAM_MBDF: MBDF_SHEET_ID,
}

RANDOM_PLAYER = "Random"
