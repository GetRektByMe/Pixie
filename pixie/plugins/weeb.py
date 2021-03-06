import discord
from Shosetsu import Shosetsu
from discord.ext import commands
from pyanimelist import PyAnimeList
from Shosetsu.errors import VNDBOneResult, VNDBNoResults

from utils import setup_file, user_agent


class Weeb:
    """A set of commands for interacting with typical weeb things like MyAnimeList and NovelUpdates"""

    def __init__(self, bot):
        self.bot = bot
        # Our instance of pyanimelist, we pass a username and password here because it's needed for their (terrible) API
        self.pyanimelist = PyAnimeList(
                            username=setup_file["weeb"]["MAL"]["username"],
                            password=setup_file["weeb"]["MAL"]["password"],
                            user_agent=user_agent
                        )

        self.shosetsu = Shosetsu()
        self.shosetsu.headers = {"User-Agent": user_agent}

    @commands.command(pass_context=True)
    async def vnsearch(self, ctx, *, vn_name: str):
        author = ctx.message.author
        avatar = author.avatar_url or author.default_avatar_url
        try:
            # List of result dictionaries
            vns = await self.shosetsu.search_vndb("v", vn_name)
        except VNDBOneResult:
            # Single dictionary
            vn = await self.shosetsu.get_novel(vn_name)
        except VNDBNoResults:
            await self.bot.send_message(ctx.message.channel, "VN not found.")
        else:
            # Put first 15 into a dictionary with ints as keys
            vns_ = dict(enumerate(vns[:15]))
            # Add all the anime names there to let the user select
            message = "```What visual novel would you like:\n"
            for vn_ in vns_.items():
                message += "[{}] {}\n".format(str(vn_[0]), vn_[1]["name"])
            message += "\nUse the number to the side of the vn as a key to select it!```"

            # Send the message for this
            await self.bot.send_message(ctx.message.channel, message)
            msg = await self.bot.wait_for_message(timeout=10.0, author=author)
            # If they don't send a message
            if not msg:
                return
            # Use this to get our dictionary
            key = int(msg.content)
            try:
                # Get the dictionary the user wants
                vn = vns_[key]
                # Get the ID that we have from searching
                id_ = vns_[key]["id"]
            except (ValueError, KeyError):
                await self.bot.send_message(ctx.message.channel, "Invalid key.")

            # Actually get the visual novel we want
            vn = await self.shosetsu.get_novel(vn["name"])

        embed = discord.Embed(
            title=vn["titles"]["english"],
            colour=discord.Colour(0x7289da),
            url="https://vndb.org/" + id_
        )

        embed.set_author(name=author, icon_url=avatar)
        embed.set_image(url=vn["img"])
        embed.add_field(name="Publishers", value=", ".join(vn["publishers"]))
        embed.add_field(name="Developers", value=", ".join(vn["developers"]))
        embed.add_field(name="Length", value=vn["length"] or "Not Stated")
        embed.add_field(name="Tags", value=", ".join({
            _ for _ in (
                vn["tags"]["content"] + vn["tags"]["technology"] + vn["tags"]["erotic"]
            )
        }), inline=False)

        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def anisearch(self, ctx, *, anime_name: str):
        author = ctx.message.author
        avatar = author.avatar_url or author.default_avatar_url
        # List of anime objects
        animes = await self.pyanimelist.search_all_anime(anime_name)
        # Put the first 15 in a dictionary with ints as keys
        animes_ = dict(enumerate(animes[:15]))
        # Add all the anime names there to let the user select
        message = "```What anime would you like:\n"
        for anime in animes_.items():
            message += "[{}] {}\n".format(str(anime[0]), anime[1].titles.jp)
        message += "\nUse the number to the side of the anime as a key to select it!```"
        await self.bot.send_message(ctx.message.channel, message)
        msg = await self.bot.wait_for_message(timeout=10.0, author=author)
        # If they don't send a message
        if not msg:
            return
        # Use this to get our anime object
        key = int(msg.content)
        try:
            # Get the anime object the user wants
            anime = animes_[key]
        except (ValueError, KeyError):
            await self.bot.send_message(ctx.message.channel, "Invalid key.")

        embed = discord.Embed(
            title=anime.titles.jp,
            colour=discord.Colour(0x7289da),
            url="https://myanimelist.net/anime/{0.id}/{0.titles.jp}".format(anime).replace(" ", "%20")
        )

        embed.set_author(name=author.display_name, icon_url=avatar)
        embed.set_image(url=anime.cover)
        embed.add_field(name="Episode Count", value=str(anime.episode_count))
        embed.add_field(name="Type", value=anime.type)
        embed.add_field(name="Status", value=anime.status)
        embed.add_field(name="Synopsis", value=anime.synopsis.split("\n\n", maxsplit=1)[0])

        await self.bot.send_message(ctx.message.channel, embed=embed)

    @commands.command(pass_context=True)
    async def mangasearch(self, ctx, *, manga_name: str):
        """
        Lets the user get data from a manga from myanimelist
        """
        author = ctx.message.author
        avatar = author.avatar_url or author.default_avatar_url
        # List of manga objects
        mangas = await self.pyanimelist.search_all_manga(manga_name)
        # Put the first 15 in a dictionary with ints as keys
        mangas_ = dict(enumerate(mangas[:15]))
        # Add all the anime names there to let the user select
        message = "```What manga would you like:\n"
        for manga in mangas_.items():
            message += "[{}] {}\n".format(str(manga[0]), manga[1].titles.jp)
        message += "\nUse the number to the side of the manga as a key to select it!```"
        await self.bot.send_message(ctx.message.channel, message)
        msg = await self.bot.wait_for_message(timeout=10.0, author=ctx.message.author)
        # If they don't send a message
        if not msg:
            return
        # Use this to get our manga object
        key = int(msg.content)
        try:
            # Get the manga object the user wants
            manga = mangas_[key]
        except (ValueError, KeyError):
            await self.bot.send_message(ctx.message.channel, "Invalid key.")

        embed = discord.Embed(
            title=manga.titles.jp,
            colour=discord.Colour(0x7289da),
            url="https://myanimelist.net/manga/{0.id}/{0.titles.jp}".format(manga).replace(" ", "%20")
        )

        embed.set_author(name=author.display_name, icon_url=avatar)
        embed.set_image(url=manga.cover)
        embed.add_field(name="Volume Count", value=str(manga.volumes))
        embed.add_field(name="Type", value=manga.type)
        embed.add_field(name="Status", value=manga.status)
        embed.add_field(name="Synopsis", value=manga.synopsis.split("\n\n", maxsplit=1)[0])

        await self.bot.send_message(ctx.message.channel, embed=embed)


class NSFW:
    """
    A class for interacting with sites like Gelbooru
    """
    def __init__(self, bot):
        pass


def setup(bot):
    bot.add_cog(Weeb(bot))
    bot.add_cog(NSFW(bot))
