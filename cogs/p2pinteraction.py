import discord
from discord.ext import commands
import aiosqlite
import random
from datetime import datetime
import sqlite3
import math

new_acc_query = """CREATE TABLE IF NOT EXISTS bank (
    user_id INT(18) PRIMARY KEY,
    wallet INTEGER,
    bank INTEGER,
    created_at VARCHAR
);"""

caught_message = [
    "You were caught breaking the window of a house by the police! You paid a fine of **500$**!",
    "You accidentally triggered the alarm! **500$** fine paid to the police!",
    "The dog noticed you sneaking into the house! The owner got alerted! **500$** reduced!",
    "You tried to pickpocket someone! But his BodyGuard saw you doing it. **500$** was paid as a fine!",
    "You tried to rob someone who works in area 51 and the guards saw you enter the restricted zone! **500$** deducted!",
    "You realized you were robbing Muzan Kibutsuji! He spared your life for **500$**!"
]

class p2pmanager(commands.Cog):

    def __init__(self,client):
        self.client = client

    def robcheckregister(self,user_id):
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

    def give_command_bg(self,user_id1,user_id2,amount): #user_id1 is giver , user_id2 is reciever
        get_p1_bal_query = f"SELECT wallet FROM bank WHERE user_id = {user_id1}"
        get_p2_bal_query = f"SELECT wallet FROM bank WHERE user_id = {user_id2}"

        with sqlite3.connect('database.db') as conn:
            bal_p1_result = conn.execute(get_p1_bal_query)
            bal_p1_tuple = bal_p1_result.fetchone()
            bal_p1 = bal_p1_tuple[0] #wallet , not bank , of user_id1
            bal_p2_result = conn.execute(get_p2_bal_query)
            bal_p2_tuple = bal_p2_result.fetchone()
            bal_p2 = bal_p2_tuple[0] #wallet , not bank , of user_id2

        if amount > bal_p1:
            return [0,0] #transfer failed
        else:
            new_p1_bal = bal_p1 - amount
            new_p2_bal = bal_p2 + amount
            set_p1_bal_query = f"UPDATE bank SET wallet = {new_p1_bal} WHERE user_id = {user_id1}"
            set_p2_bal_query = f"UPDATE bank SET wallet = {new_p2_bal} WHERE user_id = {user_id2}"
            with sqlite3.connect('database.db') as conn:
                conn.execute(set_p1_bal_query)
                conn.execute(set_p2_bal_query)
                conn.commit()

            return [2,amount] #transfer successful


    def got_robbed(self,user_id1,user_id2): #user_id1 is the one being robbed , user_id2 is robbing
        get_p1_bal_query = f"SELECT wallet FROM bank WHERE user_id = {user_id1}"
        get_p2_bal_query = f"SELECT wallet FROM bank WHERE user_id = {user_id2}"

        with sqlite3.connect('database.db') as conn:
            bal_p1_result = conn.execute(get_p1_bal_query)
            bal_p1_tuple = bal_p1_result.fetchone()
            bal_p1 = bal_p1_tuple[0] #wallet , not bank , of user_id1
            bal_p2_result = conn.execute(get_p2_bal_query)
            bal_p2_tuple = bal_p2_result.fetchone()
            bal_p2 = bal_p2_tuple[0] #wallet , not bank , of user_id2

        random_rob_amount = random.randint(math.floor(bal_p1/20),math.floor(bal_p1/10))

        rob_chance = ["y","y","y","y","y","n","y","y","y","n"]
        rob_possible = rob_chance[random.randint(0,9)]

        if bal_p1 < 2000:
            return [0,0] #victim must have atleast 2000 to be robbed
        elif bal_p2 < 1000:
            return [1,0] #robber must have atleast 1000 to rob
        elif rob_possible == "y":
            new_p1_bal = bal_p1 - random_rob_amount
            new_p2_bal = bal_p2 + random_rob_amount
            set_p1_bal_query = f"UPDATE bank SET wallet = {new_p1_bal} WHERE user_id = {user_id1}"
            set_p2_bal_query = f"UPDATE bank SET wallet = {new_p2_bal} WHERE user_id = {user_id2}"
            with sqlite3.connect('database.db') as conn:
                conn.execute(set_p1_bal_query)
                conn.execute(set_p2_bal_query)
                conn.commit()

            return [2,random_rob_amount] #rob successful
        elif rob_possible == "n":
            new_p2_bal = bal_p2 - 500
            set_p2_bal_query = f"UPDATE bank SET wallet = {new_p2_bal} WHERE user_id = {user_id2}"
            with sqlite3.connect('database.db') as conn:
                conn.execute(set_p2_bal_query)
                conn.commit()

            return [3,0] #rob unsuccessful

    @commands.command()
    @commands.cooldown(1,120,commands.BucketType.user)
    async def rob(self,ctx,member : discord.Member = None):
        if member == None:
            await ctx.send("**:x: You didn't mention a member!**")
            return
        bank_p1_check = p2pmanager.robcheckregister(self,member.id)
        bank_p2_check = p2pmanager.robcheckregister(self,ctx.author.id)
        if bank_p1_check == 1:
            await ctx.send("**:x: Mentioned user is not registered!**")
        elif bank_p2_check == 1:
            await ctx.send("**:x: You don't have a bank account!**")
        elif member == ctx.author:
            await ctx.send("**:x: Cannot rob yourself!**")
        else:
            result = p2pmanager.got_robbed(self,member.id,ctx.author.id)
            if result[0] == 0:
                await ctx.send("Victim must have atleast 2000$!")
            elif result[0] == 1:
                await ctx.send("You must have atleast 1000$ to rob someone!")
            elif result[0] == 2:
                await ctx.send(f"You successfully robbed **{result[1]}** :dollar: from **{member.display_name}!**:money_with_wings:")
            elif result[0] == 3:
                await ctx.send(caught_message[random.randint(0,5)])

    @rob.error
    async def rob_error(self,ctx,error):
        if isinstance(error,commands.MemberNotFound):
            await ctx.send("**:x: User not found**")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("**Still on cooldown**, please try again in {:.2f}s".format(error.retry_after))

    @commands.command()
    @commands.cooldown(1,3,commands.BucketType.user)
    async def give(self,ctx,member : discord.Member = None,*,amount : int = None):
        if member == None:
            await ctx.send("**:x: You didn't mention a member!**")
            return
        elif member == ctx.author:
            await ctx.send("**:x: Cannot give yourself lmao!**")
            return
        elif amount == None:
            await ctx.send("**:x: You didn't mention the amount!**")
            return
        bank_p1_check = p2pmanager.robcheckregister(self,member.id)
        bank_p2_check = p2pmanager.robcheckregister(self,ctx.author.id)
        if bank_p1_check == 1:
            await ctx.send("**:x: Mentioned user is not registered!**")
        elif bank_p2_check == 1:
            await ctx.send("**:x: You don't have a bank account!**")
        else:
            result = p2pmanager.give_command_bg(self,ctx.author.id,member.id,amount)
            if result[0] == 0:
                await ctx.send("You don't have enough money in your wallet!")
            elif result[0] == 2:
                await ctx.send(f"You have successfully transfered **{result[1]}** :dollar: to **{member.display_name}!**")

    @give.error
    async def give_error(self,ctx,error):
        if isinstance(error,commands.MemberNotFound):
            await ctx.send("**:x: User not found**")
        elif isinstance(error,commands.BadArgument):
            await ctx.send("**:x: Invalid Argument**")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("**Still on cooldown**, please try again in {:.2f}s".format(error.retry_after))

def setup(client):
    client.add_cog(p2pmanager(client))
