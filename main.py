import discord
from discord.ext import commands
import aiosqlite
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents().all()
bot = commands.Bot(command_prefix = ".", intents = intents)
bot.remove_command('help')

# List cogs to be run here
cogs = [
    'cogs.acc_manager',
    'cogs.interaction',
    'cogs.stock_changer',
    'cogs.sacc_manager',
    'cogs.sinteraction',
    'cogs.p2pinteraction'
    ]

if __name__ == '__main__':
    for cog in cogs:
        logger.info('Loading cog {}'.format(cog))
        bot.load_extension(cog)
        logger.info('Done loading cog {}'.format(cog))

@bot.event
async def on_ready():
    print("The Bot is ready!")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title = "**Render Bot**", description = "Prefix - `.`", color = 0x12dbba, timestamp = ctx.message.created_at)
    embed.add_field(name = "**Account**", value = "`new` `snew` `info` `sinfo` `bal` `sbal`")
    embed.add_field(name = "**Interaction**", value = "`rob` `dep` `sdep`")
    embed.set_thumbnail(url = bot.user.avatar_url)
    embed.set_footer(text = ctx.guild, icon_url = ctx.guild.icon_url)
    await ctx.send(embed = embed)

@bot.command()
@commands.has_permissions(administrator = True)
async def leave(ctx):
    await ctx.send("Bye bye I know you don't want me here :smiling_face_with_tear:")
    await ctx.guild.leave()

@leave.error
async def leave_error(error,ctx):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("**:x: You do not have permission to run this command**")

bot.run("bot token here")
