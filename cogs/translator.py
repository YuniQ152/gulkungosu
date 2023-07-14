from discord import Locale
from discord.ext import commands
from discord.app_commands import Translator, locale_str, TranslationContext, TranslationContextLocation


class CommandTranslator(Translator):
    async def translate(self, string: locale_str, locale: Locale, context: TranslationContext) -> str or None:

        if locale is Locale.korean:
            if context.location is TranslationContextLocation.group_name:
                if context.data.name == "calculate":
                    return "계산기"
            elif context.location is TranslationContextLocation.group_description:
                if context.data.description == "calculate":
                    return "계산기"
            elif context.location is TranslationContextLocation.command_name:
                if context.data.name == "help":
                    return "도움"
                elif context.data.name == "cofarm":
                    return "공동농장"
                elif context.data.name == "farm":
                    return "농장"
                elif context.data.name == "inventory":
                    return "인벤토리"
            elif context.location is TranslationContextLocation.command_description:
                if context.data.description == "Show the list of commands and descriptions.":
                    return "명령어 목록과 명령어의 설명을 확인합니다."
                elif context.data.description == "View co-farm info of this server.":
                    return "이 서버의 공동농장 정보를 확인합니다."
                elif context.data.description == "View farm info of user.":
                    return "농장 정보를 확인합니다."
                elif context.data.description == "View inventory summary of user.":
                    return "인벤토리의 아이템이 얼마나 무게를 차지하는지 확인합니다."
            elif context.location is TranslationContextLocation.parameter_name:
                if context.data.name == "command":
                    return "명령어"
                elif context.data.name == "member":
                    return "사용자"
            elif context.location is TranslationContextLocation.parameter_description:
                if context.data.description == "Command name or command group name to get detail of.":
                    return "명령어 또는 명령어 그룹 이름"
                elif context.data.description == "User to get farm of.":
                    return "농장을 조회할 대상. 입력하지 않을 경우 본인을 조회합니다."
                elif context.data.description == "User to get inventory of.":
                    return "인벤토리를 조회할 대상. 입력하지 않을 경우 본인을 조회합니다."
        return None

async def setup(bot: commands.Bot) -> None:
    translator = CommandTranslator()
    await bot.tree.set_translator(translator)