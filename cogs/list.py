import discord
from discord import Interaction, SelectOption
from discord.ext import commands, tasks
from discord.ui import View, Select, Button
from typing import List
from collections import deque
from math import ceil
from modules.database import *
from modules.get import *
from modules.utils import *




def list_embeds(subcommand: str("item" or "crop" or "facility" or "buff" or "option" or "step"), filter: str = "all") -> List[discord.Embed]:
    """25개 단위로 나눠서 임베드가 담린 리스트를 반환합니다"""
    
    def generate_list(subcommand: str("item" or "crop" or "facility" or "buff" or "option" or "step"), filter: str = "all"):
        """필터에 해당하는 아이템만을 찾아 리스트로 반환합니다"""

        _list = []

        if subcommand == "item":
            all_items = fetch_item_all()
            if filter == "all": # 모든 아이템
                for item in all_items:
                    _list.append(item)
            else: # 모든 아이템이 아닌 경우
                for item in all_items:
                    if item['category'] != filter and item['category'][:-2] != filter:
                        continue
                    _list.append(item)

        elif subcommand == "facility":
            all_facilities = fetch_facility_all()
            if filter == "all":
                for facility in all_facilities:
                    _list.append(facility)
            elif filter == "land":
                for facility in all_facilities:
                    if facility['size'] is not None:
                        _list.append(facility)
            elif filter == "agora":
                for facility in all_facilities:
                    if facility['size'] is None:
                        _list.append(facility)
            else:
                raise ValueError("시설물 필터 오류 (facility filter error)")
            
        elif subcommand == "crop" or subcommand == "buff" or subcommand == "option" or subcommand == "step":
            if subcommand == "crop": all = fetch_crop_all()
            elif subcommand == "buff": all = fetch_buff_all()
            elif subcommand == "option": all = fetch_option_all()
            elif subcommand == "step": all = fetch_step_all()
            for i in all:
                _list.append(i)
        
        else:
            raise ValueError("서브커멘드 유형 오류 (subcommand type error)")

        return _list

    items = generate_list(subcommand, filter)

    # 해당하는 아이템이 0개라면 검색 결과 없는 embeds 만들고 리턴
    if len(items) == 0:
        embeds = [discord.Embed(title="아이템 목록",
                                description="검색 결과 없군요. :face_with_monocle:",
                                color=discord.Color(0x57f288))]
        return embeds

    # 30개 단위로 끊어서 embed 만들고 리스트에 추가
    ITEM_PER_PAGE = 30
    embeds = []
    for i in range(ceil(len(items)/ITEM_PER_PAGE)):
        subcommand_name = {"item":"아이템", "facility":"시설물", "buff":"버프", "option":"능력치", "step":"제작 과정"}
        embed = discord.Embed(title=f"{subcommand_name[subcommand]} 목록", color=discord.Color(0x57f288))
        for j in range(3):
            field_value = ""
            for k in range(10):
                order = (i*30)+(j*10)+k
                if order >= len(items):
                    embed.add_field(name="\0", value=field_value)
                    embed.set_footer(text=f"전체 {len(items)}개 중 {i*ITEM_PER_PAGE+1}-{min((i+1)*ITEM_PER_PAGE, len(items))}개{' (필터링됨)' if filter != 'all' else ''}")
                    embeds.append(embed)
                    return embeds
                field_value += f"{order+1}. {items[order]['icon']} **{items[order]['name']}**\n"
            embed.add_field(name="\0", value=field_value)
        embed.set_footer(text=f"전체 {len(items)}개 중 {i*ITEM_PER_PAGE+1}-{min((i+1)*ITEM_PER_PAGE, len(items))}개{' (필터링됨)' if filter != 'all' else ''}")
        embeds.append(embed)
    return embeds



class ListItemView(View):
    def __init__(self, embeds: List[discord.Embed], subcommand: str) -> None:
        super().__init__(timeout=None)
        self.subcommand = subcommand
        self.filter = "all"
        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        self._current_page = 1
        self.children[0].options = self.generate_category_options(self.subcommand)
        self.children[1].disabled = True
        if self._len == 1: self.children[3].disabled = True
        self.children[2].label = f"{self._current_page} / {self._len}"

    async def update_select(self, interaction: Interaction) -> None:
        for option in self.children[0].options:
            option.default = option.value in self.filter
        await interaction.message.edit(view=self)

    async def update_buttons(self, interaction: Interaction) -> None:
        # for i in self._queue:
        #     i.set_footer(text=f"전체 {self._len} 페이지 중 {self._current_page} 페이지")
        self.children[2].label = f"{self._current_page} / {self._len}"
        if self._current_page == 1:
            self.children[1].disabled = True
        else:
            self.children[1].disabled = False
        if self._current_page == self._len:
            self.children[3].disabled = True
        else:
            self.children[3].disabled = False
        
        await interaction.message.edit(view=self)
        
    def generate_category_options(self, subcommand):
        if subcommand == "item":
            options = [SelectOption(label="모두 보기", value="all", emoji="*️⃣", default=True),
                       SelectOption(label="장비", value="equipment", emoji="🧍"),
                       SelectOption(label="작물", value="crop", emoji="🌱"),
                       SelectOption(label="묘목", value="sapling", emoji="🪴"),
                       SelectOption(label="상자", value="box", emoji="📦"),
                       SelectOption(label="음식", value="food", emoji="🍔"),
                       SelectOption(label="문서", value="document", emoji="🎫"),
                       SelectOption(label="원소", value="element", emoji="🌑"),
                       SelectOption(label="그 외", value="etc")]
        elif subcommand == "crop":
            options = [SelectOption(label="모두 보기", value="all", emoji="*️⃣", default=True)]
        elif subcommand == "facility":
            options = [SelectOption(label="모두 보기", value="all", emoji="*️⃣", default=True),
                       SelectOption(label="영토 시설물", value="land", emoji="🏘️"),
                       SelectOption(label="광장 시설물", value="agora", emoji="🚩")]
        elif subcommand == "buff":
            options = [SelectOption(label="모두 보기", value="all", emoji="*️⃣", default=True)]
        elif subcommand == "option":
            options = [SelectOption(label="모두 보기", value="all", emoji="*️⃣", default=True)]
        elif subcommand == "step":
            options = [SelectOption(label="모두 보기", value="all", emoji="*️⃣", default=True)]
        else:
            raise ValueError("서브커멘드 유형 오류 (subcommand type error)")
        return options

    @discord.ui.select(placeholder="🔎 필터링", min_values=1, max_values=1, options=[SelectOption(label="모두 보기", value="all", emoji="*️⃣", default=True)])
    async def category_select(self, interaction: Interaction, select: discord.ui.select):
        self.filter = select.values[0]
        embeds = list_embeds(self.subcommand, self.filter)
        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        self._current_page = 1
        self.children[1].disabled = True
        self.children[2].label = f"{self._current_page} / {self._len}"
        embed = self._queue[0]
        await self.update_select(interaction)
        await self.update_buttons(interaction)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(emoji='⬅')
    async def previous(self, interaction: Interaction, _):
        self._queue.rotate(1)
        embed = self._queue[0]
        self._current_page -= 1
        await self.update_buttons(interaction)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(disabled=True, style=discord.ButtonStyle.blurple)
    async def page(self, interaction: Interaction, _):
        pass

    @discord.ui.button(emoji='➡')
    async def next(self, interaction: Interaction, _):
        self._queue.rotate(-1)
        embed = self._queue[0]
        self._current_page += 1
        await self.update_buttons(interaction)
        await interaction.response.edit_message(embed=embed)

    @property
    def initial(self) -> discord.Embed:
        return self._initial


class List(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(name="목록",
                           aliases=['list', 'ㅁㄹ', 'ㅁ', 'ahrfhr', 'af', 'a'],
                           description="조건에 해당되는 항목을 나열합니다.",
                           with_app_command=True)
    async def _list(self, ctx: commands.Context):
        """
        조건에 해당되는 항목을 나열하는 명령어의 그룹입니다. 명령어 그룹 이름 뒤에 공백 한 칸과 하위 명령어 이름으로 하위 명령어를 사용할 수 있습니다.
        > 예시: `목록 아이템`
        하위 명령어의 도움말을 보려면 다음과 같이 할 수 있습니다.
        > 예시: `도움 목록 아이템` 또는 `ㄷㅇ ㅁㄹ ㅇㅇㅌ`
        """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(self._list)

    @_list.command(name="아이템",
                   aliases=['item', 'ㅇㅇㅌ', '아', 'ㅇ', '템', 'ㅌ', 'dkdlxpa', 'ddx', 'dk', 'd', 'xpa', 'x'],
                   description="아이템 목록을 확인합니다.",
                   pass_context=True)
    async def item(self, ctx: commands.Context):
        """
        아이템 목록을 확인하는 명령어입니다. 필터로 특정 아이템 범위를 찾을 수 있습니다.
        """
        embeds = list_embeds("item")
        view = ListItemView(embeds, "item")
        await ctx.reply(embed=view.initial, view=view)

    @_list.command(name="작물",
                   aliases=['crop', 'ㅈㅁ', '작', 'ㅈ', 'wa', 'wkr', 'w'],
                   description="작물 목록을 확인합니다.",
                   pass_context=True)
    async def crop(self, ctx: commands.Context):
        """
        작물 목록을 확인하는 명령어입니다.
        """
        embeds = list_embeds("crop")
        view = ListItemView(embeds, "crop")
        await ctx.reply(embed=view.initial, view=view)

    @_list.command(name="시설물",
                   aliases=['facility', 'ㅅㅅㅁ', '시', 'ㅅ', 'tta', 'tl', 't'],
                   description="시설물 목록을 확인합니다.",
                   pass_context=True)
    async def facility(self, ctx: commands.Context):
        """
        시설물 목록을 확인하는 명령어입니다. 필터로 특정 시설물 범위를 찾을 수 있습니다.
        """
        embeds = list_embeds("facility")
        view = ListItemView(embeds, "facility")
        await ctx.reply(embed=view.initial, view=view)

    @_list.command(name="버프",
                   aliases=['buff', 'ㅂㅍ', '벞', '버', 'ㅂ', 'qv', 'qjv', 'qj', 'q'],
                   description="버프 목록을 확인합니다.",
                   pass_context=True)
    async def buff(self, ctx: commands.Context):
        """
        버프 목록을 확인하는 명령어입니다.
        """
        embeds = list_embeds("buff")
        view = ListItemView(embeds, "buff")
        await ctx.reply(embed=view.initial, view=view)

    @_list.command(name="능력치",
                   aliases=['option', 'ㄴㄹㅊ', '능력', 'ㄴㄹ', '능', 'ㄴ', '옵션', 'ㅇㅅ', '옵', 'sfc', 'sf', 'smd', 's', 'dhqtus', 'dt', 'dhq'],
                   description="능력치 목록을 확인합니다.",
                   pass_context=True)
    async def option(self, ctx: commands.Context):
        """
        능력치 목록을 확인하는 명령어입니다.
        """
        embeds = list_embeds("option")
        view = ListItemView(embeds, "option")
        await ctx.reply(embed=view.initial, view=view)

    @_list.command(name="제작과정",
                   aliases=['step', '제작', 'ㅈㅈ', '제', '과', 'ㄱ', '스텝', '스탭', 'ㅅㅌ', 'wpwkr', 'ww', 'wp', 'rhk', 'r', 'tmxpq', 'tmxoq', 'tx'],
                   description="제작 과정 목록을 확인합니다.",
                   pass_context=True)
    async def step(self, ctx: commands.Context):
        """
        제작 과정 목록을 확인하는 명령어입니다.
        """
        embeds = list_embeds("step")
        view = ListItemView(embeds, "step")
        await ctx.reply(embed=view.initial, view=view)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(List(bot))
