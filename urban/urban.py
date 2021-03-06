import discord
from discord.ext import commands

import requests

from box import Box

from core.paginator import EmbedPaginatorSession


class UrbanDictionary(commands.Cog):
    """
    Let's you search on the urban dictionary.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def urban(self, ctx, *, search):
        """
        Search on the urban dictionary!
        """

        def replace_with_link(text):
            location = 0

            previous_tracked = 0

            word = ""
            in_bracket = False
            changes = ""

            for char in text:
                if char == "[":
                    in_bracket = True
                elif char == "]":
                    changes += text[previous_tracked : location + 1]
                    changes += f"(https://www.urbandictionary.com/define.php?term={word})".replace(
                        " ", "%20"
                    )

                    in_bracket = False
                    word = ""

                    previous_tracked = location + 1
                    tracked = 0
                elif in_bracket:
                    word += char
                location += 1
            changes += text[previous_tracked:]
            return changes

        r = requests.get(
            f"https://api.urbandictionary.com/v0/define?term={search}",
            headers={"User-agent": "Super Bot 9000"},
        )
        r = r.json()
        data = Box(r)

        if not data.list:
            embed = discord.Embed()
            embed.color = self.bot.error_color
            embed.title = "There is nothing here, try again."
            await ctx.send(embed=embed)
        else:
            pages = []
            for entry in data.list:
                definition = replace_with_link(entry.definition)
                example = replace_with_link(entry.example)

                ups = entry.thumbs_up
                downs = entry.thumbs_down

                page = discord.Embed(title=search)
                page.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                page.add_field(name="Definition:", value=definition, inline=False)
                page.add_field(name="Example:", value=example, inline=False)
                page.add_field(name="Upvotes:", value=ups, inline=True)
                page.add_field(name="Downvotes:", value=downs, inline=True)

                pages.append(page)
            session = EmbedPaginatorSession(ctx, *pages)
            await session.run()


def setup(bot):
    bot.add_cog(UrbanDictionary(bot))
