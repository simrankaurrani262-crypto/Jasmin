# NSFW FEATURES DISABLED FOR SAFETY
# All NSFW commands have been removed to comply with Telegram Terms of Service

from Emilia.custom_filter import register
from Emilia.functions.admins import is_admin
from Emilia.mongo.nsfw_mongo import is_nsfw_on, nsfw_off, nsfw_on
from Emilia.utils.decorators import *
import Emilia.strings as strings


@register(pattern="addnsfw")
@logging
async def add_nsfw(event):
    """NSFW feature has been disabled."""
    await event.reply("⚠️ **NSFW features have been permanently disabled from this bot for safety and compliance with Telegram Terms of Service.**")
    return "NSFW_DISABLED", None, None


@register(pattern="rmnsfw")
@logging
async def rem_nsfw(event):
    """NSFW feature has been disabled."""
    await event.reply("⚠️ **NSFW features have been permanently disabled from this bot.**")
    return "NSFW_DISABLED", None, None


@register(pattern="blowjob|bj")
async def blowjob(event):
    """NSFW feature disabled."""
    await event.reply("❌ **This NSFW command has been disabled.**")


@register(pattern="trap")
async def trap(event):
    """NSFW feature disabled."""
    await event.reply("❌ **This NSFW command has been disabled.**")


@register(pattern="(nsfwwaifu|nwaifu)")
async def nsfwwaifu(event):
    """NSFW feature disabled."""
    await event.reply("❌ **This NSFW command has been disabled.**")


@register(pattern="(nsfwneko|nneko)")
async def nsfwneko(event):
    """NSFW feature disabled."""
    await event.reply("❌ **This NSFW command has been disabled.**")


@register(pattern="lewd")
async def lewd(event):
    """NSFW feature disabled."""
    await event.reply("❌ **This NSFW command has been disabled.**")
    
