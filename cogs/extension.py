import os
from discord.ext import commands


class ReloadCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(name="reload", aliases=['ㄹㄹ', 'ff'], hidden=True)
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, sync: bool = False):
        try:
            for filename in os.listdir("./cogs"):
                if filename.endswith(".py") and filename != "__init__.py":
                    await self.bot.unload_extension(f"cogs.{filename[:-3]}")
                    await self.bot.load_extension(f"cogs.{filename[:-3]}")
            if sync:
                await self.bot.tree.sync()
            await ctx.reply("All cogs have been reloaded.")

        except Exception as e:
            await ctx.reply(f"An error occurred while reloading cogs: {e}")
            return
        
    @reload.error
    async def collection_power_error(self, ctx, error):
        if isinstance(error, commands.NotOwner):
            pass
    

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ReloadCog(bot))
