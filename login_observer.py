import asyncio
from reactivex import Observer
from data import Config
from rcon import RconContext
from rcon_listener import RconListener
from parsers import parse_event, GROK_LOGIN_EVENT


class LoginObserver(Observer[str]):
    _config: Config

    def __init__(self, config: Config) -> None:
        self._config = config
        super().__init__()

    def get_tag(self, tag: str):
        return self._config.tag_format.format(tag)

    async def handle_tag(self, event_data: dict[str, str]):
        playfab_id = event_data["playfabId"]
        user_name = event_data["userName"]
        target_tag = self._config.tags.get(playfab_id, None)
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
        await asyncio.sleep(self._config.salute_timer) # so player can see his own salute
        async with asyncio.timeout(10):
            async with RconContext() as client:
                await client.execute(f"say {target_salute}")

    def on_next(self, value: str) -> None:
        (success, event_data) = parse_event(value, GROK_LOGIN_EVENT)
        if not success:
            return
        event_text = event_data["eventText"].lower()
        if event_text.startswith("logged out"):
            return
        asyncio.create_task(self.handle_salute(event_data))
        asyncio.create_task(self.handle_tag(event_data))


if __name__ == "__main__":
    login_listener = RconListener("login")
    manager = LoginObserver(
        Config({"PLAYFABID": "MORBIUS"}, {"PLAYFABID": "IT'S MORBIN TIME"})
    )
    login_listener.subscribe(manager)

    asyncio.run(login_listener.start())
