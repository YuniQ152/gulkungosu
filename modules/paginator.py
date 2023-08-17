import discord
from typing import List
from collections import deque



class PageButtonView(discord.ui.View):
    def __init__(self, embeds: List[discord.Embed]) -> None:
        super().__init__(timeout=None)
        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._len = len(embeds)
        self._current_page = 1
        self.children[0].disabled = True
        self.children[1].label = f"{self._current_page} / {self._len}"
        self.children[1].label = f"{self._current_page} / {self._len}"
        # self._queue[0].set_footer(text=f"전체 {self._len} 페이지 중 {self._current_page} 페이지")


    async def update_buttons(self, interaction: discord.Interaction) -> None:
        # for i in self._queue:
        #     i.set_footer(text=f"전체 {self._len} 페이지 중 {self._current_page} 페이지")
        self.children[1].label = f"{self._current_page} / {self._len}"
        if self._current_page == 1:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False
        if self._current_page == self._len:
            self.children[2].disabled = True
        else:
            self.children[2].disabled = False
        
        await interaction.message.edit(view=self)

    @discord.ui.button(emoji='⬅')
    async def previous(self, interaction: discord.Interaction, _):
        self._queue.rotate(1)
        embed = self._queue[0]
        self._current_page -= 1
        await self.update_buttons(interaction)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(disabled=True, style=discord.ButtonStyle.blurple)
    async def page(self, interaction: discord.Interaction, _):
        pass

    @discord.ui.button(emoji='➡')
    async def next(self, interaction: discord.Interaction, _):
        self._queue.rotate(-1)
        embed = self._queue[0]
        self._current_page += 1
        await self.update_buttons(interaction)
        await interaction.response.edit_message(embed=embed)

    @property
    def initial(self) -> discord.Embed:
        return self._initial
