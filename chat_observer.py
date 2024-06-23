import asyncio
from reactivex import Observer
from rcon import RconContext
from parsers import GROK_CHAT_EVENT, parse_event
from playtime_client import PlaytimeClient


class ChatObserver(Observer[str]):
    playtime_client: PlaytimeClient

    def __init__(self, playtime_client: PlaytimeClient) -> None:
        self.playtime_client = playtime_client
        super().__init__()

    async def handle_playtime(self, playfab_id: str, user_name: str):
        user_playtime = await self.playtime_client.get_playtime(playfab_id)
        full_msg = ""
        if user_playtime < 1:
            full_msg = f"{user_name} has no recorded playtime"
        else:
            unit = "mins" if user_playtime <= 60 else "hours"
            time = user_playtime if user_playtime < 60 else round(user_playtime / 60, 1)
            time_comp = f"{time} {unit}"
            user_comp = f"{user_name} has played"
            full_msg = " ".join([user_comp, time_comp])
        async with RconContext() as client:
            await client.execute(f"say {full_msg}")

    def on_next(self, value: str) -> None:
        (success, event_data) = parse_event(value, GROK_CHAT_EVENT)
        if not success:
            return
        message = event_data.get("message")
        if message == ".playtime":
            user_name = event_data["userName"]
            playfab_id = event_data["playfabId"]
            asyncio.create_task(self.handle_playtime(playfab_id, user_name))


# todo: add local test run here
