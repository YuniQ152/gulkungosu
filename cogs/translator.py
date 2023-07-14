from discord import Locale
from discord.ext import commands
from discord.app_commands import Translator, locale_str, TranslationContext, TranslationContextLocation


class CommandTranslator(Translator):
    async def translate(self, string: locale_str, locale: Locale, context: TranslationContext) -> str or None:

        if context.location is TranslationContextLocation.parameter_name:
            if context.data.name == "command":
                return "명령어"
            elif context.data.name == "member":
                return "사용자"
            elif context.data.name == "target":
                return "대상"
            elif context.data.name == "keyword":
                return "검색어"
            elif context.data.name == "crop":
                return "작물"
            elif context.data.name == "collected":
                return "박제개수"
        return None

async def setup(bot: commands.Bot) -> None:
    translator = CommandTranslator()
    await bot.tree.set_translator(translator)