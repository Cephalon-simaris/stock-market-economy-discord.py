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

new_sacc_query = """CREATE TABLE IF NOT EXISTS sharebank (
    user_id INT(18) PRIMARY KEY,
    balance INTEGER,
    created_at VARCHAR
);"""

class interaction(commands.Cog):

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

    def scheckregister(self,user_id):
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

    def sdep_execute(self,user_id,amount):
        get_sbal_query = f"SELECT balance FROM sharebank WHERE user_id = {user_id};"
        get_bal_query = f"SELECT wallet FROM bank WHERE user_id = {user_id};"

        with sqlite3.connect('database.db') as conn:
            sbal_result = conn.execute(get_sbal_query)
            sbal_tuple = sbal_result.fetchone()
            sbal = sbal_tuple[0]
            bal_result = conn.execute(get_bal_query)
            bal_tuple = bal_result.fetchone()
            bal = bal_tuple[0]

        if amount > bal:
            return 0 #insufficient amount in wallet
        elif amount <= bal:
            new_sbal = sbal + amount
            new_bal = bal - amount
            set_sbal_query = f"UPDATE sharebank SET balance = {new_sbal} WHERE user_id = {user_id};"
            set_bal_query = f"UPDATE bank SET wallet = {new_bal} WHERE user_id = {user_id};"

            with sqlite3.connect('database.db') as conn:
                conn.execute(set_sbal_query)
                conn.execute(set_bal_query)
                conn.commit()
            
            return 1 #requirements met

    def swidthdraw_execute(self,user_id,amount):
        get_sbal_query = f"SELECT balance FROM sharebank WHERE user_id = {user_id};"
        get_bal_query = f"SELECT wallet FROM bank WHERE user_id = {user_id};"

        with sqlite3.connect('database.db') as conn:
            sbal_result = conn.execute(get_sbal_query)
            sbal_tuple = sbal_result.fetchone()
            sbal = sbal_tuple[0]
            bal_result = conn.execute(get_bal_query)
            bal_tuple = bal_result.fetchone()
            bal = bal_tuple[0]

        if amount > sbal:
            return 0 #insufficient amount in share balance
        elif amount <= sbal:
            new_sbal = sbal - amount
            new_bal = bal + amount
            set_sbal_query = f"UPDATE sharebank SET balance = {new_sbal} WHERE user_id = {user_id};"
            set_bal_query = f"UPDATE bank SET wallet = {new_bal} WHERE user_id = {user_id};"

            with sqlite3.connect('database.db') as conn:
                conn.execute(set_sbal_query)
                conn.execute(set_bal_query)
                conn.commit()
            
            return 1 #requirements met

    def bank_to_wallet(self,user_id,amount):
        get_wallet_query = f"SELECT wallet FROM bank WHERE user_id = {user_id};"
        get_bank_query = f"SELECT bank FROM bank WHERE user_id = {user_id};"

        with sqlite3.connect('database.db') as conn:
            bank_result = conn.execute(get_bank_query)
            bank_tuple = bank_result.fetchone()
            bank = bank_tuple[0]
            wallet_result = conn.execute(get_wallet_query)
            wallet_tuple = wallet_result.fetchone()
            wallet = wallet_tuple[0]

        if amount > bank:
            return 0 #insufficient amount in bank
        elif amount <= bank:
            new_bank = bank - amount
            new_wallet = wallet + amount
            set_bank_query = f"UPDATE bank SET bank = {new_bank} WHERE user_id = {user_id};"
            set_wallet_query = f"UPDATE bank SET wallet = {new_wallet} WHERE user_id = {user_id};"

            with sqlite3.connect('database.db') as conn:
                conn.execute(set_bank_query)
                conn.execute(set_wallet_query)
                conn.commit()
            
            return 1 #requirements met

    def wallet_to_bank(self,user_id,amount):
        get_wallet_query = f"SELECT wallet FROM bank WHERE user_id = {user_id};"
        get_bank_query = f"SELECT bank FROM bank WHERE user_id = {user_id};"

        with sqlite3.connect('database.db') as conn:
            bank_result = conn.execute(get_bank_query)
            bank_tuple = bank_result.fetchone()
            bank = bank_tuple[0]
            wallet_result = conn.execute(get_wallet_query)
            wallet_tuple = wallet_result.fetchone()
            wallet = wallet_tuple[0]

        if amount > wallet:
            return 0 #insufficient amount in wallet
        elif amount <= wallet:
            new_bank = bank + amount
            new_wallet = wallet - amount
            set_bank_query = f"UPDATE bank SET bank = {new_bank} WHERE user_id = {user_id};"
            set_wallet_query = f"UPDATE bank SET wallet = {new_wallet} WHERE user_id = {user_id};"

            with sqlite3.connect('database.db') as conn:
                conn.execute(set_bank_query)
                conn.execute(set_wallet_query)
                conn.commit()
            
            return 1 #requirements met


    @commands.command()
    async def sdep(self,ctx,amount : int = None):
        bank_check = interaction.checkregister(self,ctx.author.id)
        sbank_check = interaction.scheckregister(self,ctx.author.id)
        if sbank_check == 1:
            if bank_check == 1:
                await ctx.send("You don't have a share and a bank account!")
            else:
                await ctx.send("You don't have a share account!")
        elif amount == None:
            await ctx.send("You didn't mention the amount you want to deposit!")
        else:
            did_it_work = interaction.sdep_execute(self,ctx.author.id,amount)
            if did_it_work == 0:
                await ctx.send("You have insufficient amount in your wallet than specified amount!")
            else:
                await ctx.send(":white_check_mark: Transaction successful! Check your balance!")
        
    @sdep.error
    async def sdep_error(self,ctx,error):
        if isinstance(error,commands.BadArgument):
            await ctx.send(":x: **Invalid argument passed!**")

    @commands.command()
    async def swithdraw(self,ctx,amount : int = None):
        bank_check = interaction.checkregister(self,ctx.author.id)
        sbank_check = interaction.scheckregister(self,ctx.author.id)
        if sbank_check == 1:
            if bank_check == 1:
                await ctx.send("You don't have a share and a bank account!")
            else:
                await ctx.send("You don't have a share account!")
        elif amount == None:
            await ctx.send("You didn't mention the amount you want to deposit!")
        else:
            did_it_work = interaction.swidthdraw_execute(self,ctx.author.id,amount)
            if did_it_work == 0:
                await ctx.send("You have insufficient amount in your share balance than specified amount!")
            else:
                await ctx.send(":white_check_mark: Transaction successful! Check your balance!")
        
    @swithdraw.error
    async def swithdraw_error(self,ctx,error):
        if isinstance(error,commands.BadArgument):
            await ctx.send(":x: **Invalid argument passed!**")

    @commands.command()
    async def withdraw(self,ctx,amount : int = None):
        bank_check = interaction.checkregister(self,ctx.author.id)
        if bank_check == 1:
            await ctx.send("You don't have a bank account!")
        elif amount == None:
            await ctx.send("You didn't mention the amount you want to withdraw!")
        else:
            did_it_work = interaction.bank_to_wallet(self,ctx.author.id,amount)
            if did_it_work == 0:
                await ctx.send("You have insufficient amount in your bank than specified amount!")
            else:
                await ctx.send(":white_check_mark: Withdrawal successful! Check your balance!")

    @withdraw.error
    async def withdraw_error(self,ctx,error):
        if isinstance(error,commands.BadArgument):
            await ctx.send(":x: **Invalid argument passed!**")

    @commands.command()
    async def dep(self,ctx,amount : int = None):
        bank_check = interaction.checkregister(self,ctx.author.id)
        if bank_check == 1:
            await ctx.send("You don't have a bank account!")
        elif amount == None:
            await ctx.send("You didn't mention the amount you want to deposit!")
        else:
            did_it_work = interaction.wallet_to_bank(self,ctx.author.id,amount)
            if did_it_work == 0:
                await ctx.send("You have insufficient amount in your wallet than specified amount!")
            else:
                await ctx.send(":white_check_mark: Deposit successful! Check your balance!")

    @dep.error
    async def dep_error(self,ctx,error):
        if isinstance(error,commands.BadArgument):
            await ctx.send(":x: **Invalid argument passed!**")


def setup(client):
    client.add_cog(interaction(client))