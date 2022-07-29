import discord

from commonbot.utils import strip_words, get_first_word

from config import CMD_PREFIX, HE_PRONOUN, SHE_PRONOUN, THEY_PRONOUN, ANY_PRONOUN, ASK_PRONOUN
from utils import requires_admin

PRONOUNS = {
    "He/Him": HE_PRONOUN,
    "She/Her": SHE_PRONOUN,
    "They/Them": THEY_PRONOUN,
    "Any": ANY_PRONOUN,
    "Ask": ASK_PRONOUN,
}

class PronounWidgetButton(discord.ui.Button):
    def __init__(self, txt: str, row: int):
        custom_id = f"pronoun_ui:{txt}"
        super().__init__(style=discord.ButtonStyle.primary, label=txt, row=row, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        # view: PronounWidget = self.view

        role_id = PRONOUNS[self.label]
        role = discord.utils.get(interaction.user.guild.roles, id=role_id)
        if interaction.user.get_role(role_id):
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"{self.label} role removed!", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"{self.label} role added!", ephemeral=True)

class PronounWidget(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for pronoun, _ in PRONOUNS.items():
            self.add_item(PronounWidgetButton(pronoun, 0))

@requires_admin
async def post_widget(message: discord.Message) -> str:
    try:
        payload = strip_words(message.content, 1)
        chan_id = get_first_word(payload)
        channel = discord.utils.get(message.guild.channels, id=int(chan_id))
        await channel.send("Press the buttons to add/remove the role!", view=PronounWidget())
        return ""
    except ValueError:
        return f"I was unable to find a channel ID in that message. `{CMD_PREFIX}roles CHAN_ID`"