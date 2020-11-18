from dataclasses import dataclass
import urllib.parse


@dataclass
class Player:
    activision_id: str
    display_name: str
    name: str

    def get_urlencoded_display_name(self) -> str:
        return urllib.parse.quote(self.display_name)

    def get_urlencoded_activision_username(self) -> str:
        full_username = self.display_name
        if self.activision_id:
            full_username += "#" + self.activision_id
        return urllib.parse.quote(full_username)
