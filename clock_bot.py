import json
import pytz
from asyncio import sleep
from datetime import datetime

import discord
from discord.ext import tasks


client = discord.Client()
with open("config.json", "rb") as f:
    config = json.loads(f.read())


@tasks.loop(minutes=5)
async def update_time_channels():
    await client.wait_until_ready()
    time_str = datetime.now(tz=pytz.timezone(config["timezone"])).strftime("%H:%M%p %Z")
    for channel_id in config["channel_ids"]:
        await client.get_channel(int(channel_id)).edit(name=f"🕒 ~{time_str}")


def get_5m_sync_delay():
    """Returns the delay in seconds to the next 5-minute sync point"""
    current_dt = datetime.now()
    delay_seconds = 0

    cminutes = 5 - (current_dt.minute % 5)  # Remaining minutes
    if cminutes != 5:  # Add time if minutes remaining
        delay_seconds += cminutes * 60

    delay_seconds += (
        60 - current_dt.second
    ) - 60  # Remaining seconds sync'd to start of minute

    return delay_seconds if delay_seconds >= 0 else 0


@update_time_channels.before_loop
async def pre_update_time_channels():
    await client.wait_until_ready()
    await sleep(get_5m_sync_delay())


update_time_channels.start()
client.run(config["token"])
