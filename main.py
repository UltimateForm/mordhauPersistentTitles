import os
import asyncio
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorCollection
from reactivex import operators
from data import Config, load_config, save_config
from database import load_db
from parsers import GROK_LOGIN_EVENT, parse_date, parse_event
from rcon_listener import RconListener
from login_observer import LoginObserver
from chat_observer import ChatObserver
import logger
from session_topic import SessionTopic
from playtime_client import PlaytimeClient

load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=".", intents=intents)
bot_channel = int(os.environ.get("BOT_CHANNEL", None))
config: Config


def make_embed(ctx: commands.Context):
    embed = discord.embeds.Embed(title=ctx.command, color=3447003)  # blue
    embed.set_footer(text="persistentTitles")
    return embed


@bot.command()
async def ping(ctx: commands.Context):
    await ctx.message.reply(":ping_pong:")


# TODO: create custom decorator so we dont have to repeat error handling in all the below commands


@bot.command("setTagFormat")
async def set_tag_format(ctx: commands.Context, arg_format: str):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    embed.add_field(name="ArgFormat", value=arg_format)
    try:
        if "{0}" not in arg_format:
            raise ValueError(
                f"`{arg_format}` is not a valid format. Must include tag placeholder (`{{0}}`) in the format string."
            )
        config.tag_format = arg_format
        save_config(config)
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed)


@bot.command("setSaluteTimer")
async def set_salute_timer(ctx: commands.Context, arg_timer: int):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    embed.add_field(name="ArgFormat", value=f"{arg_timer} seconds")
    try:
        config.salute_timer = arg_timer
        save_config(config)
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed)


@bot.command("addTag")
async def add_tag(ctx: commands.Context, arg_playfab_id: str, arg_tag: str):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    embed.add_field(name="PlayfabId", value=arg_playfab_id)
    embed.add_field(name="Tag", value=arg_tag)
    try:
        config.tags[arg_playfab_id] = arg_tag
        save_config(config)
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed)


@bot.command("addRename")
async def add_rename(ctx: commands.Context, arg_playfab_id: str, arg_rename: str):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    embed.add_field(name="PlayfabId", value=arg_playfab_id)
    embed.add_field(name="Rename", value=arg_rename)
    try:
        config.rename[arg_playfab_id] = arg_rename
        save_config(config)
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed)


@bot.command("addPlaytimeTag")
async def add_playtime_tag(ctx: commands.Context, arg_minutes: int, arg_tag: str):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    embed.add_field(name="Min minutes played", value=arg_minutes)
    embed.add_field(name="Tag", value=arg_tag)
    try:
        config.playtime_tags[str(arg_minutes)] = arg_tag
        save_config(config)
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed)


@bot.command("removeTag")
async def remove_tag(ctx: commands.Context, arg_playfab_id: str):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    embed.add_field(name="PlayfabId", value=arg_playfab_id)
    try:
        current_tag = config.tags.get(arg_playfab_id, None)
        if not current_tag:
            raise ValueError(
                f"PlayfabId {arg_playfab_id} doesn't have any registered tag"
            )
        embed.add_field(name="RemovedTag", value=current_tag)
        config.tags.pop(arg_playfab_id, None)
        save_config(config)
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed)


@bot.command("removeRename")
async def remove_rename(ctx: commands.Context, arg_playfab_id: str):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    embed.add_field(name="PlayfabId", value=arg_playfab_id)
    try:
        current_rename = config.rename.get(arg_playfab_id, None)
        if not current_rename:
            raise ValueError(
                f"PlayfabId {arg_playfab_id} doesn't have any registered rename"
            )
        embed.add_field(name="RemovedRename", value=current_rename)
        config.rename.pop(arg_playfab_id, None)
        save_config(config)
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed)


@bot.command("removePlaytimeTag")
async def remove_playtime_tag(ctx: commands.Context, arg_minutes: str):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    embed.add_field(name="Min minutes played", value=arg_minutes)
    try:
        current_tag = config.playtime_tags.get(arg_minutes, None)
        if not current_tag:
            raise ValueError(
                f"Min minutes played {arg_minutes} doesn't have any registered tag"
            )
        embed.add_field(name="RemovedTag", value=current_tag)
        config.playtime_tags.pop(arg_minutes, None)
        save_config(config)
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed)


@bot.command("addSalute")
async def add_salute(ctx: commands.Context, arg_playfab_id: str, arg_salute: str):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    embed.add_field(name="PlayfabId", value=arg_playfab_id)
    embed.add_field(name="Salute", value=arg_salute, inline=False)
    try:
        config.salutes[arg_playfab_id] = arg_salute
        save_config(config)
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed)


@bot.command("removeSalute")
async def remove_salute(ctx: commands.Context, arg_playfab_id: str):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    embed.add_field(name="PlayfabId", value=arg_playfab_id)
    try:
        current_salute = config.salutes.get(arg_playfab_id, None)
        if not current_salute:
            raise ValueError(
                f"PlayfabId {arg_playfab_id} doesn't have any registered salute"
            )
        embed.add_field(name="RemovedSalute", value=current_salute, inline=False)
        config.salutes.pop(arg_playfab_id, None)
        save_config(config)
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed)


@bot.command("ptConf")
async def get_config(ctx: commands.Context):
    if bot_channel and ctx.channel.id != bot_channel:
        return
    embed = make_embed(ctx)
    too_long: bool = False
    json_code: str = ""
    try:
        config_json = json.dumps(config.__dict__, indent=2)
        json_code = f"```{config_json}```"
        too_long = len(json_code) >= 1024

        embed.add_field(
            name="Config",
            value=json_code if not too_long else "Too long, sent separately",
            inline=False,
        )
        embed.add_field(name="Success", value=True, inline=False)
    except Exception as e:
        embed.add_field(name="Success", value=False, inline=False)
        embed.add_field(name="Error", value=str(e), inline=False)
        embed.color = 15548997  # red
    await ctx.message.reply(embed=embed, content=json_code if too_long else None)


config = load_config()


async def main():
    logger.use_date_time_logger()
    playtime_collection: AsyncIOMotorCollection | None = None
    playtime_client: PlaytimeClient | None = None
    live_sessions_collection: AsyncIOMotorCollection | None = None
    playtime_enabled = False
    db = load_db()
    if db:
        logger.info("Enabling playtime titles as DB is loaded")
        (live_sessions_collection, playtime_collection) = db
        playtime_client = PlaytimeClient(playtime_collection)
        playtime_enabled = True
    else:
        logger.info("Keeping playtime titles disabled as DB is not loaded")
    login_listener = RconListener("login")
    chat_listener = RconListener("chat")
    login_observer = LoginObserver(config, playtime_client)
    login_listener.pipe(operators.filter(lambda x: x.startswith("Login:"))).subscribe(
        login_observer
    )

    if playtime_enabled:
        chat_observer = ChatObserver(config, playtime_client)
        chat_listener.subscribe(chat_observer)
        session_topic = SessionTopic(live_sessions_collection)
        session_topic.subscribe(playtime_client)

        def session_topic_login_handler(event: str):
            (success, event_data) = parse_event(event, GROK_LOGIN_EVENT)
            if not success:
                logger.debug(f"Failure at parsing login event {event}")
                return
            logger.debug(f"LOGIN EVENT: {event_data}")
            order = event_data["order"]
            playfab_id = event_data["playfabId"]
            user_name = event_data["userName"]
            date = parse_date(event_data["date"])
            if order == "in":
                asyncio.create_task(session_topic.login(playfab_id, user_name, date))
            elif order == "out":
                asyncio.create_task(session_topic.logout(playfab_id, date))

        login_listener.pipe(
            operators.filter(lambda x: x.startswith("Login:"))
        ).subscribe(session_topic_login_handler)

    tasks = [login_listener.start(), bot.start(token=os.environ.get("D_TOKEN"))]
    if playtime_enabled:
        tasks.append(chat_listener.start())
    await asyncio.gather(*tasks)


asyncio.run(main())
