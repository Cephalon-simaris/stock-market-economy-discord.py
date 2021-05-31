from sqlite3.dbapi2 import connect
import discord
from discord.ext import commands
import aiosqlite
import random
from datetime import datetime
import sqlite3

share_stock_maker_query = """CREATE TABLE IF NOT EXISTS share_stock (
    companyname VARCHAR PRIMARY KEY,
    stock INTEGER
);"""

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

class sinteraction(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.stocksetup()

    def stocksetup(self):
        setup_check_query2 = "SELECT * FROM share_stock;"
        company_data_query_format2 = ("INSERT INTO share_stock(companyname,stock) VALUES(?,?)")
        company_data_query_data2 = lambda name : (f"Company {name}",10)
        alphabets2 = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

        with sqlite3.connect('database.db') as conn:
            conn.execute(purchased_shares_table_query)
            conn.execute(share_stock_maker_query)
            cur = conn.execute(setup_check_query2)
            if cur.fetchone() == None:

                for i in range(len(alphabets2)):
                    query2 = company_data_query_data2(alphabets2[i])
                    conn.execute(company_data_query_format2,query2)

                conn.commit()
            else:
                return

    def buycheck(self,companyname,price,bal):
        if bal < price:
            return "transaction not valid"
        elif bal > price:
            return "transaction valid"

    def sbal_buy(self,user_id,balance,price):
        set_balance = balance - price
        reduce_query = f"UPDATE sharebank SET balance = {set_balance} WHERE user_id = {user_id};"
        with sqlite3.connect('database.db') as conn:
            conn.execute(reduce_query)
            conn.commit()

    def sbal_sell(self,user_id,balance,price):
        set_balance = balance + price
        reduce_query = f"UPDATE sharebank SET balance = {set_balance} WHERE user_id = {user_id};"
        with sqlite3.connect('database.db') as conn:
            conn.execute(reduce_query)
            conn.commit()

    def boughtshare(self,user_id,companyname,stock,bal,price): #to decrease stock and validating transaction
        check_validation = sinteraction.buycheck(self,companyname,price,bal)
        if check_validation == "transaction valid":
            if stock == 0:
                return 0 #no stock
            else:
                stock = stock - 1
                purchase_query = f"UPDATE share_stock SET stock = {stock} WHERE companyname = \"{companyname}\";"
                share_adder_query = ("INSERT INTO your_shares(user_id,companyname,bought_at_price) VALUES(?,?,?)")
                share_adder_data = (user_id,companyname,price)

                with sqlite3.connect('database.db') as conn:
                    conn.execute(purchase_query)
                    conn.execute(share_adder_query,share_adder_data)
                    conn.commit()
                
                sinteraction.sbal_buy(self,user_id,bal,price)
                return 1 #transaction valid
        else:
            return 2 #transaction not valid

    def soldshare(self,user_id,companyname,stock,bal,price): #to increase stock and validating transaction

        if stock == 10:
            return 0 #max limit reached
        else:
            stock = stock + 1
            purchase_query = f"UPDATE share_stock SET stock = {stock} WHERE companyname = \"{companyname}\";"
            stock_delete_query = f"DELETE FROM your_shares WHERE user_id = {user_id} AND companyname = \"{companyname}\";"

            with sqlite3.connect('database.db') as conn:
                conn.execute(purchase_query)
                conn.execute(stock_delete_query)
                conn.commit()

            sinteraction.sbal_sell(self,user_id,bal,price)
            return 1 #sold

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
            return 1 #does not

    def companyrates(self,companyname):
        existance_check_query = f"SELECT price FROM share_price WHERE companyname = \"{companyname}\";"

        with sqlite3.connect('database.db') as conn:
            cur = conn.execute(existance_check_query)
            result = cur.fetchall()

        if result == []:
            return "No Company found!"
        else:
            return result[0][0]

    @commands.command(aliases = ["r","rate","currrates"])
    async def rates(self,ctx,*,stockname : str = None):
        check_register = sinteraction.scheckregister(self,ctx.author.id)
        if stockname == None:
            await ctx.send("**:x: You did not mention which stock you want to check!**")
        elif check_register == 1:
            await ctx.send("**:x: You need a share account to view price!**")
        else:
            check = sinteraction.companyrates(self,f"{stockname}")
            if check == "No Company found!":
                await ctx.send(":x: **No Company found!**")
            else:
                em = discord.Embed(description = f":office: **Current Price of {stockname} :** `{check}` :dollar:",color = discord.Colour.green())
                await ctx.send(embed = em)

    @commands.command()
    async def buy(self,ctx,*,stockname : str = None):
        check_register = sinteraction.scheckregister(self,ctx.author.id)
        if stockname == None:
            await ctx.send("**:x: You did not mention which stock you want to buy!**")
        elif check_register == 1:
            await ctx.send("**:x: User not registered**")
        else:
            get_bal_query = f"SELECT balance FROM sharebank WHERE user_id = {str(ctx.author.id)}"
            get_stock_query = f"SELECT stock FROM share_stock WHERE companyname = \"{stockname}\""
            get_stock_price_query = f"SELECT price FROM share_price WHERE companyname = \"{stockname}\""

            try:

                async with aiosqlite.connect("database.db") as conn:
                    result = await conn.execute(get_stock_query)
                    fetch = await result.fetchone()
                    stock_amount = fetch[0]
                    result2 = await conn.execute(get_bal_query)
                    fetch2 = await result2.fetchone()
                    bal = fetch2[0]
                    result3 = await conn.execute(get_stock_price_query)
                    fetch3 = await result3.fetchone()
                    price = fetch3[0]

                conclusion = sinteraction.boughtshare(self,ctx.author.id,f"{stockname}",stock_amount,bal,price)
                if conclusion == 0:
                    await ctx.send("Sorry maxmimum number of shares have been sold out! :(")
                elif conclusion == 1:
                    await ctx.send(f"Congratulations! The share {stockname} has been bought by you!")
                else:
                    await ctx.send("Sorry you don't have enough money to buy this!")
            except:
                await ctx.send("**:x: company not found**")

    @commands.command()
    async def sell(self,ctx,*,stockname : str = None):
        check_register = sinteraction.scheckregister(self,ctx.author.id)
        if stockname == None:
            await ctx.send("**:x: You did not mention which stock you want to buy!**")
        elif check_register == 1:
            await ctx.send("**:x: User not registered**")
        else:
            get_bal_query = f"SELECT balance FROM sharebank WHERE user_id = {str(ctx.author.id)}"
            get_stock_query = f"SELECT stock FROM share_stock WHERE companyname = \"{stockname}\""
            get_stock_price_query = f"SELECT price FROM share_price WHERE companyname = \"{stockname}\""

            try:

                async with aiosqlite.connect("database.db") as conn:
                    result = await conn.execute(get_stock_query)
                    fetch = await result.fetchone()
                    stock_amount = fetch[0]
                    result2 = await conn.execute(get_bal_query)
                    fetch2 = await result2.fetchone()
                    bal = fetch2[0]
                    result3 = await conn.execute(get_stock_price_query)
                    fetch3 = await result3.fetchone()
                    price = fetch3[0]

                conclusion = sinteraction.soldshare(self,ctx.author.id,f"{stockname}",stock_amount,bal,price)
                if conclusion == 0:
                    await ctx.send("Sorry the company was out of stock :(")
                elif conclusion == 1:
                    await ctx.send(f"Congratulations! The share {stockname} has been sold!")
            except:
                await ctx.send("**:x: company not found**")

def setup(client):
    client.add_cog(sinteraction(client))