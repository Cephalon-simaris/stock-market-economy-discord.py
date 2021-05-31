import discord
from discord.errors import DiscordException
from discord.ext import commands
import aiosqlite
import random
from datetime import datetime
import sqlite3

new_sacc_query = """CREATE TABLE IF NOT EXISTS sharebank (
    user_id INT(18) PRIMARY KEY,
    balance INTEGER,
    created_at VARCHAR
);"""

purchased_shares_table_query = """CREATE TABLE IF NOT EXISTS your_shares (
    user_id INT(18),
    companyname VARCHAR,
    bought_at_price INTEGER
);"""

class shareaccmanager(commands.Cog):

    def __init__(self,client):
        self.client = client

    def checkregister(self,user_id):
        existance_check_query = f"SELECT user_id FROM sharebank;"
        
        with sqlite3.connect('database.db') as conn:
            conn.execute(new_sacc_query)
            cur = conn.execute(existance_check_query)
            result = cur.fetchall()
            
        for i in range(len(result)):
            if user_id == result[i][0]:
                return 0 #account exists
        else:
            return 1 #account does not exist


    @commands.command(aliases = ["sregister"])
    async def snew(self,ctx):

        check_register = shareaccmanager.checkregister(self,ctx.author.id)

        if check_register == 1:
            time = str(datetime.utcnow())

            sql = ("INSERT INTO sharebank(user_id,balance,created_at) VALUES(?,?,?)")
            val = (str(ctx.author.id), 0, f"{time[0:19]} UTC")

            async with aiosqlite.connect('database.db') as conn:
                await conn.execute(new_sacc_query)
                await conn.execute(sql,val)
                await conn.commit()

            embed = discord.Embed(title = ":white_check_mark: Share account Created! successfully!",description = "type `.sinfo` to see your account details!",color = discord.Colour.green(),timestamp = ctx.message.created_at)
            await ctx.send(embed = embed)
        else:
            await ctx.send("Share account already exists!")

    @commands.command()
    async def sinfo(self,ctx,* ,member : discord.Member = None):

        if member == None:
            member = ctx.author

        check_register = shareaccmanager.checkregister(self,member.id)

        if check_register == 0:
            get_info_query = f"SELECT user_id,created_at FROM sharebank WHERE user_id = {member.id}"

            async with aiosqlite.connect('database.db') as conn:
                result = await conn.execute(get_info_query)
                fetch = await result.fetchall()
            
            embed = discord.Embed(title = f"**Info of {member}**", colour = member.color , timestamp = ctx.message.created_at)
            embed.add_field(name = "Share account Created on :", value = ":calendar_spiral: "+fetch[0][1])
            embed.set_thumbnail(url = member.avatar_url)
            await ctx.send(embed = embed)

        else:
            await ctx.send("**:x: User is not registered for share market**")

    @sinfo.error
    async def sinfo_error(self,ctx,error):
        if isinstance(error,commands.MemberNotFound):
            await ctx.send("**:x: User not found**")

    @commands.command(aliases = ["Sbal"])
    async def sbal(self,ctx,* ,member : discord.Member = None):

        if member == None:
            member = ctx.author

        check_register = shareaccmanager.checkregister(self,member.id)

        if check_register == 0:
            get_info_query = f"SELECT user_id,balance FROM sharebank WHERE user_id = {member.id}"

            async with aiosqlite.connect('database.db') as conn:
                result = await conn.execute(get_info_query)
                fetch = await result.fetchall()
            
            embed = discord.Embed(title = f"**Share balance of {member.display_name}** :moneybag:", description = f":bank: **Balance** : `{str(fetch[0][1])}` :dollar:", colour = discord.Colour.green() , timestamp = ctx.message.created_at)
            await ctx.send(embed = embed)

        else:
            await ctx.send("**:x: User is not registered for share market**")

    @sbal.error
    async def sbal_error(self,ctx,error):
        if isinstance(error,commands.MemberNotFound):
            await ctx.send("**:x: User not found**")

    @commands.command()
    async def myshares(self,ctx):
        check_register = shareaccmanager.checkregister(self,ctx.author.id)

        if check_register == 0:
            get_shares_query = f"SELECT companyname,bought_at_price FROM your_shares WHERE user_id = {ctx.author.id};"
            get_curr_share_price = lambda company_name : f"SELECT price FROM share_price WHERE companyname = \"{company_name}\""

            async with aiosqlite.connect('database.db') as conn:
                result = await conn.execute(get_shares_query)
                fetch = await result.fetchall() #format - [('Company A', 43), ('Company B', 4)]

            if len(fetch) == 0:
                await ctx.send("You currently don't have any shares!")
            
            else:
                embed = discord.Embed(title = ":office: **Your owned shares**", color = ctx.author.color, timestamp = ctx.message.created_at)
                
                async with aiosqlite.connect('database.db') as conn:
                    for i in range(0,len(fetch)):
                        result2 = await conn.execute(get_curr_share_price(fetch[i][0]))
                        fetch2 = await result2.fetchone()
                        embed.add_field(
                            name = f"{fetch[i][0]}",
                            value = f":money_with_wings: **Share Bought at : **`{fetch[i][1]}` :dollar:\n:bar_chart: **Current price : **`{fetch2[0]}` :dollar:",
                            inline = False
                        )
                await ctx.send(embed = embed)

        else:
            await ctx.send("**:x: User is not registered for share market**")

def setup(client):
    client.add_cog(shareaccmanager(client))