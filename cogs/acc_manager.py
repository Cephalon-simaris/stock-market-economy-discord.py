import discord
from discord.ext import commands
import aiosqlite
import random
from datetime import datetime
import sqlite3

new_acc_query = """CREATE TABLE IF NOT EXISTS bank (
    user_id INT(18) PRIMARY KEY,
    wallet INTEGER,
    bank INTEGER,
    created_at VARCHAR
);"""

class accmanager(commands.Cog):

    def __init__(self,client):
        self.client = client

    def checkregister(self,user_id):
        existance_check_query = f"SELECT user_id FROM bank;"
        
        with sqlite3.connect('database.db') as conn:
            conn.execute(new_acc_query)
            cur = conn.execute(existance_check_query)
            result = cur.fetchall()
            
        for i in range(len(result)):
            if user_id == result[i][0]:
                return 0 #account exists
        else:
            return 1 #account does not exist


    @commands.command(aliases = ["register","Register","New"])
    async def new(self,ctx):

        check_register = accmanager.checkregister(self,ctx.author.id)

        if check_register == 1:
            time = str(datetime.utcnow())

            sql = ("INSERT INTO bank(user_id,wallet,bank,created_at) VALUES(?,?,?,?)")
            val = (str(ctx.author.id),100, 100, f"{time[0:19]} UTC")

            async with aiosqlite.connect('database.db') as conn:
                await conn.execute(new_acc_query)
                await conn.execute(sql,val)
                await conn.commit()

            embed = discord.Embed(title = "Account Created! successfully!",description = "type `.info` to see your account details!",color = discord.Colour.green(),timestamp = ctx.message.created_at)
            await ctx.send(embed = embed)
        else:
            await ctx.send("Account already exists!")

    @commands.command(aliases = ["about","Info","About"])
    async def info(self,ctx,* ,member : discord.Member = None):

        if member == None:
            member = ctx.author

        check_register = accmanager.checkregister(self,member.id)

        if check_register == 0:
            get_info_query = f"SELECT user_id,created_at FROM bank WHERE user_id = {member.id}"

            async with aiosqlite.connect('database.db') as conn:
                result = await conn.execute(get_info_query)
                fetch = await result.fetchall()
            
            embed = discord.Embed(title = f"**Info of {member}**", colour = member.color , timestamp = ctx.message.created_at)
            embed.add_field(name = "Account Created on :", value = ":calendar_spiral: "+fetch[0][1])
            embed.set_thumbnail(url = member.avatar_url)
            await ctx.send(embed = embed)

        else:
            await ctx.send("**:x: User is not registered**")

    @info.error
    async def info_error(self,ctx,error):
        if isinstance(error,commands.MemberNotFound):
            await ctx.send("**:x: User not found**")

    @commands.command(aliases = ["Bal"])
    async def bal(self,ctx,* ,member : discord.Member = None):

        if member == None:
            member = ctx.author

        check_register = accmanager.checkregister(self,member.id)

        if check_register == 0:
            get_info_query = f"SELECT user_id,wallet,bank FROM bank WHERE user_id = {member.id}"

            async with aiosqlite.connect('database.db') as conn:
                result = await conn.execute(get_info_query)
                fetch = await result.fetchall()
            
            embed = discord.Embed(title = f"**Balance of {member.display_name}** :moneybag:", description = f":credit_card: **Wallet** : `{str(fetch[0][1])}` :dollar:\n:bank: **Bank** : `{str(fetch[0][2])}` :dollar:", colour = discord.Colour.green() , timestamp = ctx.message.created_at)
            await ctx.send(embed = embed)

        else:
            await ctx.send("**:x: User is not registered**")

    @bal.error
    async def bal_error(self,ctx,error):
        if isinstance(error,commands.MemberNotFound):
            await ctx.send("**:x: User not found**")

def setup(client):
    client.add_cog(accmanager(client))