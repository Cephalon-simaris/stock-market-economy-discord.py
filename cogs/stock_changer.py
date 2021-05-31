import discord
from discord.ext import commands
from discord.ext import tasks
import aiosqlite
import random
from datetime import datetime
import sqlite3
import asyncio

stock_market_maker_query = """CREATE TABLE IF NOT EXISTS share_price (
    companyname VARCHAR PRIMARY KEY,
    price INTEGER
);"""

class stockchanger(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.setup()
        self.stockchange.start()

    def randomizer(self,companyname,price):
        random_increase = random.randint(0,20)
        random_decrease = random.randint(0,20)
        choice_list = [random_increase,random_decrease]
        random_choice = random.randint(0,1)
        
        if random_choice == 0:
            price = price + random_increase
        else:
            price = price - random_decrease
            if price < 0:
                price = 0

        randomizer_query = f"UPDATE share_price SET price = {price} WHERE companyname = \"{companyname}\";"

        with sqlite3.connect('database.db') as conn:
            conn.execute(randomizer_query)
            conn.commit()

    def setup(self):
        setup_check_query = "SELECT * FROM share_price;"
        company_data_query_format = ("INSERT INTO share_price(companyname,price) VALUES(?,?)")
        company_data_query_data = lambda name : (f"Company {name}",10)
        alphabets = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

        with sqlite3.connect('database.db') as conn:
            conn.execute(stock_market_maker_query)
            cur = conn.execute(setup_check_query)
            if cur.fetchone() == None:

                for i in range(len(alphabets)):
                    query = company_data_query_data(alphabets[i])
                    conn.execute(company_data_query_format,query)

                conn.commit()
            else:
                return

    @tasks.loop(seconds=60)
    async def stockchange(self):
        await self.bot.wait_until_ready()
        company_name = lambda name : f"Company {name}"
        alphabets = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        curr_prize = lambda na : f"SELECT price FROM share_price WHERE companyname = \"Company {na}\""

        async with aiosqlite.connect('database.db') as conn:
            await conn.execute(stock_market_maker_query)

            for i in range(len(alphabets)):
                name_of_company = company_name(alphabets[i])
                company_price_query = curr_prize(alphabets[i])
                result = await conn.execute(company_price_query)
                fetch = await result.fetchone()
                stockchanger.randomizer(self,name_of_company,fetch[0])

            await conn.commit()
            
            
def setup(client):
    client.add_cog(stockchanger(client))