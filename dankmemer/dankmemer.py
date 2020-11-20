# -*- coding: utf-8 -*-
import asyncio
import typing
import urllib
from io import BytesIO

import aiohttp
import discord
import validators
from redbot.core import Config, commands
from redbot.core.utils.predicates import MessagePredicate

from .converters import ImageFinder


async def tokencheck(ctx):
    token = await ctx.bot.get_shared_api_tokens("imgen")
    return bool(token.get("authorization"))


class DankMemer(commands.Cog):
    """Dank Memer Commands."""

    __version__ = "0.0.18"

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=95932766180343808, force_registration=True)
        self.config.register_global(url="https://imgen.flaree.xyz/api")
        self.session = aiohttp.ClientSession()
        self.headers = {}

    async def red_get_data_for_user(self, *, user_id: int):
        # this cog does not story any data
        return {}

    async def red_delete_data_for_user(self, *, requester, user_id: int) -> None:
        # this cog does not story any data
        pass

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def initalize(self):
        self.api = await self.config.url()
        token = await self.bot.get_shared_api_tokens("imgen")
        self.headers = {"Authorization": token.get("authorization")}

    @commands.Cog.listener()
    async def on_red_api_tokens_update(self, service_name, api_tokens):
        if service_name == "imgen":
            self.headers = {"Authorization": api_tokens.get("authorization")}

    async def send_error(self, ctx, data):
        await ctx.send(f"Oops, an error occured. `{data['error']}`")

    async def get(self, ctx, url, json=False):
        async with ctx.typing():
            async with self.session.get(self.api + url, headers=self.headers) as resp:
                if resp.status == 200:
                    if json:
                        return await resp.json()
                    file = await resp.read()
                    file = BytesIO(file)
                    file.seek(0)
                    return file
                if resp.status == 404:
                    return {
                        "error": "Server not found, ensure the correct URL is setup and is reachable. "
                    }
                try:
                    return await resp.json()
                except aiohttp.ContentTypeError:
                    return {"error": "Server may be down, please try again later."}

    async def send_img(self, ctx, image):
        if not ctx.channel.permissions_for(ctx.me).send_messages:
            return
        if not ctx.channel.permissions_for(ctx.me).attach_files:
            await ctx.send("I don't have permission to attach files.")
            return
        try:
            await ctx.send(file=image)
        except aiohttp.ClientOSError:
            await ctx.send("An error occured sending the picture.")

    def parse_text(self, text):
        return urllib.parse.quote(text)

    @commands.command()
    async def dankmemersetup(self, ctx):
        """Instructions on how to setup DankMemer."""
        msg = (
            "You must host your own instance of imgen or apply for a publically available instance.\n"
            f"You can then set the url endpoints using the `{ctx.clean_prefix}dmurl <url>` command. (Support will be limited if using your own instance.)\n\n"
            f"You can set the token using `{ctx.clean_prefix}set api imgen authorization <key>`"
        )
        await ctx.maybe_send_embed(msg)

    @commands.is_owner()
    @commands.command()
    async def dmurl(self, ctx, *, url: commands.clean_content(fix_channel_mentions=True)):
        """Set the DankMemer API Url.

        Ensure the url ends in API without the backslash - Example: https://imgen.flaree.xyz/api
        Only use this if you have an instance already.
        """
        if not validators.url(url):
            return await ctx.send(f"{url} doesn't seem to be a valid URL. Please try again.")
        await ctx.send(
            "This has the ability to make every command fail if the URL is not reachable and/or not working. Only use this if you're experienced enough to understand. Type yes to continue, otherwise type no."
        )
        try:
            pred = MessagePredicate.yes_or_no(ctx, user=ctx.author)
            await ctx.bot.wait_for("message", check=pred, timeout=20)
        except asyncio.TimeoutError:
            await ctx.send("Exiting operation.")
            return

        if pred.result:
            await self.config.url.set(url)
            await ctx.tick()
            await self.initalize()
        else:
            await ctx.send("Operation cancelled.")

    @commands.check(tokencheck)
    @commands.command()
    async def abandon(self, ctx, *, text: commands.clean_content(fix_channel_mentions=True)):
        """Abandoning your son?"""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/abandon?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "abandon.png"
        await self.send_img(ctx, discord.File(data))
    
    @commands.check(tokencheck)
    @commands.command()
    async def abesaale(self, ctx, image: ImageFinder = None):
        """Abe saale."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/abesaale?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "abesaale.png"
        await self.send_img(ctx, discord.File(data))                   

    @commands.check(tokencheck)
    @commands.command(aliases=["aborted"])
    async def abort(self, ctx, image: ImageFinder = None):
        """All the reasons why X was aborted."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/aborted?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "abort.png"
        await self.send_img(ctx, discord.File(data))

    @commands.check(tokencheck)
    @commands.command()
    async def affect(self, ctx, image: ImageFinder = None):
        """It won't affect my baby."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/affect?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "affect.png"
        await self.send_img(ctx, discord.File(data))   

    @commands.check(tokencheck)
    @commands.command()
    async def brazzers(self, ctx, image: ImageFinder = None):
        """Brazzerfy your image."""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/brazzers?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "brazzers.png"
        await self.send_img(ctx, discord.File(data))
    
    @commands.check(tokencheck)
    @commands.command()
    async def bsdk(self, ctx, image: ImageFinder = None):
        """Bhosdike"""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/bsdk?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "bsdk.png"
        await self.send_img(ctx, discord.File(data))                   
    
    @commands.check(tokencheck)
    @commands.command()
    async def kabhi(self, ctx, *, text: commands.clean_content(fix_channel_mentions=True)):
        """kabhi aisa lagta hai"""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/kabhi?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "kabhi.png"
        await self.send_img(ctx, discord.File(data))                   
    
    @commands.check(tokencheck)
    @commands.command()
    async def kyabe(self, ctx, image: ImageFinder = None):
        """dissapointed pakistani guy"""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/kyabe?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "kyabe.png"
        await self.send_img(ctx, discord.File(data))   
                       
    @commands.check(tokencheck)
    @commands.command()
    async def kyahaal(self, ctx, image: ImageFinder = None):
        """Are maa chudi padi hai"""
        if image is None:
            image = ctx.author.avatar_url_as(static_format="png")
        data = await self.get(ctx, f"/kyahaal?avatar1={image}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "kyahaal.png"
        await self.send_img(ctx, discord.File(data))                      

    @commands.check(tokencheck)
    @commands.command(aliases=["em"])
    async def emergencymeeting(
        self, ctx, *, text: commands.clean_content(fix_channel_mentions=True)
    ):
        """Call an emergency meeting."""
        text = self.parse_text(text)
        data = await self.get(ctx, f"/emergencymeeting?text={text}")
        if isinstance(data, dict):
            return await self.send_error(ctx, data)
        data.name = "emergencymeeting.png"
        await self.send_img(ctx, discord.File(data))


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i : i + n]
