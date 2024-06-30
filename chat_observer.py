import asyncio
from reactivex import Observer
from data import Config
from compute import (
    compute_gate_text,
    compute_next_gate_text,
    compute_time_txt,
    slice_text_array_at_total_length,
)
from rcon import RconContext
from parsers import GROK_CHAT_EVENT, parse_event
from playtime_client import PlaytimeClient


class ChatObserver(Observer[str]):
    playtime_client: PlaytimeClient
    _config: Config

    def __init__(self, config: Config, playtime_client: PlaytimeClient) -> None:
        self.playtime_client = playtime_client
        self._config = config
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

    async def handle_rank(self, playfab_id: str, user_name: str):
        user_playtime = await self.playtime_client.get_playtime(playfab_id)
        global_rank = self._config.tags.get("*", None)
        full_msg = ""
        (_, rank_txt) = compute_gate_text(user_playtime, self._config.playtime_tags)
        full_msg += f"{user_name} rank: {rank_txt or global_rank}"
        (next_rank_minutes, next_rank_txt) = compute_next_gate_text(
            user_playtime, self._config.playtime_tags
        )
        if next_rank_txt is not None:
            full_msg += (
                f"; Next: {next_rank_txt} at {compute_time_txt(next_rank_minutes)}"
            )
        async with RconContext() as client:
            await client.execute(f"say {full_msg}")

    # todo: fix bug here, slice_text_array_at_total_length is not accurate with new length calculation, doesnt account for new lines
    async def handle_ranks(self):
        playtime_tags = self._config.playtime_tags
        keys = sorted(
            [int(key) for key in list(playtime_tags.keys()) if key.isnumeric()]
        )
        full_msg_comps = [
            f"{playtime_tags.get(str(key))}: {compute_time_txt(key)}" for key in keys
        ]
        if 0 not in keys:
            global_rank = self._config.tags.get("*", None)
            if global_rank:
                full_msg_comps.insert(0, f"{global_rank}: Base rank")
        full_msg = "\n".join(full_msg_comps)
        full_msg_len = len(full_msg)
        head = "Ranks on playtime:\n"
        expected_mh_len = len(head) + full_msg_len
        if expected_mh_len > 280:
            partitioned = slice_text_array_at_total_length(280, full_msg_comps)
            cont = False
            for partition in partitioned:
                msg = "\n".join(partition)
                head = head if not cont else ""
                async with RconContext() as client:
                    await client.execute(f"say {head}{msg}")
                cont = True
        else:
            async with RconContext() as client:
                await client.execute(f"say {head}{full_msg}")

    def on_next(self, value: str) -> None:
        (success, event_data) = parse_event(value, GROK_CHAT_EVENT)
        if not success:
            return
        message = event_data.get("message")
        playfab_id = event_data["playfabId"]
        user_name = event_data["userName"]
        if message == ".playtime":
            asyncio.create_task(self.handle_playtime(playfab_id, user_name))
        elif message == ".rank":
            asyncio.create_task(self.handle_rank(playfab_id, user_name))
        elif message == ".ranks":
            asyncio.create_task(self.handle_ranks())


# todo: add local test run here
