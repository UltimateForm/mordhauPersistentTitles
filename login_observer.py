import asyncio
from reactivex import Observer
import numpy as np
from data import Config
from rcon import RconContext
from rcon_listener import RconListener
from parsers import parse_event, GROK_LOGIN_EVENT
from playtime_client import PlaytimeClient


class LoginObserver(Observer[str]):
    _config: Config
    playtime_client: PlaytimeClient | None

    def __init__(
        self, config: Config, playtime_client: PlaytimeClient | None = None
    ) -> None:
        self._config = config
        self.playtime_client = playtime_client
        super().__init__()

    def get_tag(self, tag: str):
        return self._config.tag_format.format(tag)

    def compute_playtime_tag(self, minutes_played: int) -> str | None:
        playtime_tags = self._config.playtime_tags
        playtime_keys = list(playtime_tags.keys())
        # todo: ditch numpy alltogether
        # we could sort it by highest and then do next([x for x in keys if x <= minutes_played])
        gates = np.fromiter(
            [int(key) for key in playtime_keys if key.isnumeric()], np.uint64
        )
        lesser_gates = gates[gates <= minutes_played]
        if len(lesser_gates) == 0:
            return None
        highest_lesser_gate = lesser_gates.max()
        return playtime_tags[str(highest_lesser_gate)]

    async def handle_tag(self, event_data: dict[str, str]):
        playfab_id = event_data["playfabId"]
        user_name = event_data["userName"]
        target_tag = self._config.tags.get(playfab_id, None)
        if target_tag is None and self.playtime_client is not None:
            minutes_played = await self.playtime_client.get_playtime(playfab_id)
            target_tag = self.compute_playtime_tag(minutes_played)
        if target_tag is None:
            target_tag = self._config.tags.get("*", None)
        if not target_tag:
            return
        tag_formatted = self.get_tag(target_tag)
        sanitized_username = user_name.replace(tag_formatted, "")
        new_user_name = " ".join([tag_formatted, sanitized_username])
        async with asyncio.timeout(10):
            async with RconContext() as client:
                await client.execute(f"renameplayer {playfab_id} {new_user_name}")

    async def handle_salute(self, event_data: dict[str, str]):
        playfab_id = event_data["playfabId"]
        target_salute = self._config.salutes.get(playfab_id, None)
        if not target_salute:
            return
        await asyncio.sleep(
            self._config.salute_timer
        )  # so player can see his own salute
        async with asyncio.timeout(10):
            async with RconContext() as client:
                await client.execute(f"say {target_salute}")

    def on_next(self, value: str) -> None:
        (success, event_data) = parse_event(value, GROK_LOGIN_EVENT)
        if not success:
            return
        order = event_data["order"].lower()
        if order == "out":
            return
        asyncio.create_task(self.handle_salute(event_data))
        asyncio.create_task(self.handle_tag(event_data))


if __name__ == "__main__":
    login_listener = RconListener("login")
    manager = LoginObserver(
        Config({"PLAYFABID": "MORBIUS"}, {"PLAYFABID": "IT'S MORBIN TIME"}, {})
    )
    login_listener.subscribe(manager)

    asyncio.run(login_listener.start())
