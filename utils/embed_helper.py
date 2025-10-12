import discord

def make_embed(bot, title: str, description=None, color=discord.Color.blurple(), footer=True, image=None, thumbnail=None):

    if isinstance(description, list):
        description = '\n'.join(f"> {line}" for line in description)
    description = description or " "

    embed = discord.Embed(title=title, description=description, color=color)

    if image:
        embed.set_image(url=image)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if footer:
        embed.set_footer(text='Class Companion', icon_url=bot.user.display_avatar.url)

    return embed
