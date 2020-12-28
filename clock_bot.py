import json
import pytz
from asyncio import sleep
from datetime import datetime
from sys import stderr

import discord
from discord.ext import tasks


client = discord.Client()
with open("config.json", "rb") as f:
    config = json.loads(f.read())
SYNC_MINUTE = config["sync_minute"]
if SYNC_MINUTE < 1:
    print("Invalid sync minute", file=stderr)
    exit(-1)


@tasks.loop(minutes=SYNC_MINUTE)
async def update_time_channels():
    await client.wait_until_ready()
    time_str = datetime.now(tz=pytz.timezone(config["timezone"])).strftime("%H:%M%p %Z")
    for channel_id in config["channel_ids"]:
        await client.get_channel(int(channel_id)).edit(name=f"🕒 ~{time_str}")


def get_sync_delay(sync_minute=5):
    """
        Returns the delay in seconds to the next sync point
        Example:
          5 would sync at 5, 10, 15, 20...
    """
    current_dt = datetime.now()
    delay_seconds = 0

    cminutes = sync_minute - (current_dt.minute % sync_minute)  # Remaining minutes
    if cminutes != sync_minute:  # Add time if minutes remaining
        delay_seconds += cminutes * 60

    delay_seconds += (
        60 - current_dt.second
    ) - 60  # Remaining seconds sync'd to start of minute

    return delay_seconds if delay_seconds >= 0 else 0


@update_time_channels.before_loop
async def pre_update_time_channels():
    await client.wait_until_ready()
    await sleep(get_sync_delay(SYNC_MINUTE))


update_time_channels.start()
client.run(config["token"])
