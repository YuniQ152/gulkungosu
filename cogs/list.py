import discord
from discord import Interaction, SelectOption
from discord.ext import commands, tasks
from discord.ui import View, Select, Button
from typing import List
from collections import deque
from modules.database import *
from modules.get import *
from modules.utils import *



def item_embeds(category_filter: str = "all") -> List[discord.Embed]:
    all_items = fetch_item_all()
    items = []
    if category_filter == "all": # 모든 아이템
        for item in all_items:
            items.append(item)
    else: # 모든 아이템이 아닌 경우
        for item in all_items:
            if item['category'] != category_filter and item['category'][:-2] != category_filter:
                continue
            items.append(item)

    # 해당하는 아이템이 0개라면 검색 결과 없는 embeds 만들고 리턴
    if len(items) == 0:
        embeds = [discord.Embed(title="아이템 목록",
                                description="검색 결과 없군요. :face_with_monocle:",
                                color=discord.Color(0x57f288))]
        return embeds

    # 25개 단위로 끊어서 embed 만들고 리스트에 추가
    embeds = []
    for i in range(0, len(items), 25):
        description = ""
        for j in range(0, min(len(items)-i, 25), 1):
            description += f"{i+j+1}. {items[i+j]['icon']} **{items[i+j]['name']}**\n"
        embed=discord.Embed(title="아이템 목록",
                            description=description[:1999],
                            color=discord.Color(0x57f288))
        embed.set_footer(text=f"전체 {len(items)}개 중 {i+1}-{min(i+25, len(items))}개")
        embeds.append(embed)
    
    return embeds


class FilterView(View):
    def __init__(self, embeds: List[discord.Embed]) -> None:
        super().__init__(timeout=None)
        self.category_filter = "all"
        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        self._current_page = 1
        self.children[1].disabled = True
        self.children[2].label = f"{self._current_page} / {self._len}"

    async def update_select(self, interaction: Interaction) -> None:
        for option in self.children[0].options:
            option.default = option.value in self.category_filter
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

    @discord.ui.select(placeholder="🔎 아이템 필터링",
                       min_values=1,
                       max_values=1,
                       options=[SelectOption(label="모두 보기", value="all", emoji="*️⃣", default=True),
                                SelectOption(label="장비", value="equipment", emoji="🧍"),
                                SelectOption(label="작물", value="crop", emoji="🌱"),
                                SelectOption(label="묘목", value="sapling", emoji="🪴"),
                                SelectOption(label="상자", value="box", emoji="📦"),
                                SelectOption(label="음식", value="food", emoji="🍔"),
                                SelectOption(label="문서", value="document", emoji="🎫"),
                                SelectOption(label="원소", value="element", emoji="🌑"),
                                SelectOption(label="그 외", value="etc")])
    async def category_select(self, interaction: Interaction, select: discord.ui.select):
        self.category_filter = select.values[0]
        embeds = item_embeds(self.category_filter)
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
                           aliases=['ㅁㄹ', 'ㅁ', 'ahrfhr', 'af', 'a'],
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
                   aliases=['ㅇㅇㅌ', '아', 'ㅇ', '템', 'ㅌ', 'dkdlxpa', 'ddx', 'dk', 'd', 'xpa', 'x'],
                   description="아이템 목록을 확인합니다.",
                   pass_context=True)
    async def item(self, ctx: commands.Context):
        """
        아이템 목록을 확인하는 명령어입니다. 필터로 특정 아이템 범위를 찾을 수 있습니다.
        """

        embeds = item_embeds()
        view = FilterView(embeds)
        await ctx.reply(embed=view.initial, view=view)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(List(bot))
