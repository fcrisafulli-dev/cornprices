import discord
from discord.ext import commands
import pickle
from random import randint
from numpy import sin,cos
import datetime

companies_file = 'company.p'
portfolios_file = 'user.p'

bot = commands.Bot(command_prefix='!')
no_portfolio_err = "you dont have a portfolio registered. Type !register to create one"

class Company:
    def __init__(self,name):
        self.name = name
        
        self.angle = randint(1,10)
        self.violence = randint(5,9)
        self.rang = randint(2,8)
        self.bankrupt = 1
        self.expires = ((self.angle/100)*12000)+10
        self.prospects = ['Starting Anew',0]
        if self.angle == 1:
            self.angle = -10
            self.expires = ((1/100)*12000)+10

        self.shares_out = 0
        print(name,self.expires,self.angle)

    def get_value(self,t):
        v = (50 + (t/self.angle) + (sin(t)*self.rang) + (sin(10*t)/self.violence) + cos(t)) * self.bankrupt
        return round(v,2)

class Portfolio:
    def __init__(self,user):
        self.user = user
        self.shares = {}
        self.money = 1000

try:
    companies = pickle.load(open(companies_file, 'rb'))
except FileNotFoundError:
    c1 = Company('LongCorn')
    c2 = Company('CornYELLOW')
    c3 = Company('SuperCorn')
    c4 = Company('CornTech')
    companies = {
            'longcorn' : c1,
            'cornyellow' : c2,
            'supercorn' : c3,
            'corntech' : c4
            }

try:
    portfolios = pickle.load(open(portfolios_file, 'rb'))
except FileNotFoundError:
    portfolios = {}

def get_value(t,x,rang,violence):
    return 50 + (t/x) + (sin(t)*rang) + (sin(10*t)/violence) + cos(t)

def save_game():
    pickle.dump( companies, open( companies_file , "wb" ) )
    pickle.dump( portfolios, open( portfolios_file , "wb" ) )

@bot.event
async def on_ready():
    global atime
    atime = datetime.datetime.now()
    print(f'Logged in as {bot.user}')

@bot.command()
async def save(ctx):
    save_game()
    await ctx.send("Saved Corn Prices!")

@bot.command()
async def cornhelp(ctx):
    await ctx.message.author.send("""
HELP:
!register -> Creates your portfolio 

!money -> Shows your money

!buy {companyname} {ammount} -> Buys shares

!sell {companyname} {ammount} -> Sells shares

!shares -> Shows Your Portfolio

!cornprices -> Gets CORN PRICES
""")

@bot.command()
async def register(ctx):
    if str(ctx.message.author) in portfolios:
        await ctx.send(f"{ctx.message.author.name}, you already have a portfolio!" ) 
    else:
        author = ctx.message.author
        portfolios[str(author)] = Portfolio(author.name)
        await ctx.send(f"{author.name}, your portfolio has been created. Type !cornhelp for more") 

@bot.command()
async def cornprices(ctx):
    global time
    prices = discord.Embed(title="Corn Prices", description="!cornhelp for more", color=0xffff00)
    for key in companies.keys():
        company = companies[key]
        prices.add_field(name=company.name, value=f"${company.get_value(time)} | {company.prospects[0]} {company.prospects[1]} ", inline=False)
    await ctx.send(embed=prices)

@bot.command()
async def shares(ctx):
    if str(ctx.message.author) not in portfolios:
        await ctx.send(f"{ctx.message.author.name} {no_portfolio_err}" ) 
        return

    shares = discord.Embed(title=f"{ctx.author.name}'s Shares", description="#Shares, Percent Owned", color=0xff9900)
    for key in companies.keys():
        company = companies[key]
        if company.name.lower() in portfolios[str(ctx.message.author)].shares:
            percent = (portfolios[str(ctx.message.author)].shares[company.name.lower()] / (company.shares_out+1)) * 100
            shares.add_field(name=company.name, value=f"${portfolios[str(ctx.message.author)].shares[company.name.lower()]} | {round(percent,2)}% ", inline=False)
    await ctx.send(embed=shares)

@bot.command()
async def money(ctx):
    try:
        cash = portfolios[str(ctx.message.author)].money
        money = discord.Embed(title=f"{ctx.author.name}'s Cash", description=f"${cash}", color=0xff0000)
        await ctx.send(embed=money)
    except KeyError:
        await ctx.send(f"{ctx.message.author.name} {no_portfolio_err}" ) 

@bot.command()
async def debug(ctx):
    for key in companies.keys():
        company = companies[key]
        print(company.shares_out,company.expires)

@bot.command()
async def buy(ctx, inc, amnt: int):
    company = inc.lower()
    if str(ctx.message.author) not in portfolios:
        await ctx.send(f"{ctx.message.author.name} {no_portfolio_err}" ) 
        return
    

    if company in companies:

        if companies[company].prospects[0] == 'BANKRUPT':
            await ctx.send(f"{companies[company].name} is bankrupt!" ) 
            return

        price = companies[company].get_value(time) * amnt
        if portfolios[str(ctx.message.author)].money >= price:
            if company in portfolios[str(ctx.message.author)].shares:
                portfolios[str(ctx.message.author)].shares[company] += amnt
            else:
                portfolios[str(ctx.message.author)].shares[company] = amnt
            companies[company].shares_out += amnt
            portfolios[str(ctx.message.author)].money -= price
            await ctx.send(f"{ctx.message.author.name} bought {amnt} shares from {company} for ${price}." )
        else:
            await ctx.send(f"You cant afford that. price: ${price} your balance: ${portfolios[str(ctx.message.author)].money}") 

    else:
        await ctx.send(f"The company {company} doesnt exist" ) 
        return


@bot.command()
async def sell(ctx, inc, amnt: int):
    company = inc.lower()
    if str(ctx.message.author) not in portfolios:
        await ctx.send(f"{ctx.message.author.name} {no_portfolio_err}" ) 
        return

    
    if company in companies:

        if companies[company].prospects[0] == 'BANKRUPT':
            await ctx.send(f"{companies[company].name} is bankrupt!" ) 
            return
        global time
        price = companies[company].get_value(time) * amnt
        if company in portfolios[str(ctx.message.author)].shares:
            if portfolios[str(ctx.message.author)].shares[company] >= amnt:
                portfolios[str(ctx.message.author)].shares[company] -= amnt
                companies[company].shares_out -= amnt
                portfolios[str(ctx.message.author)].money += price
                await ctx.send(f"{ctx.message.author.name} sold {amnt} shares to {company} for ${price}." )
            else:
                await ctx.send(f"You dont have enough shares. You have {portfolios[str(ctx.message.author)].shares[company]}.") 
        else:
            await ctc.send(f"You dont own any shares from {company}! Buy some with '!buy {company} ammount'")

    else:
        await ctx.send(f"The company {company} doesnt exist" ) 
        return

@bot.event
async def on_message(message):
    global time
    global atime
    now = datetime.datetime.now()
    td = (now - atime).seconds 
    if td > 15:
        atime = datetime.datetime.now()
    if message.author == bot.user:
        return
    else:
        try:
            time += (td // 15) * .1
        except:
            time = 1 
    if time % 2 == 0:
        save_game()
    for key in companies.keys():
        companies[key].expires -= .2
        if companies[key].expires < 0 and companies[key].prospects[0] != "BANKRUPT":
            companies[key].prospects = ["BANKRUPT", "" ]
            companies[key].bankrupt = 0
            for key2 in portfolios.keys():
                try:
                    del portfolios[key2].shares[companies[key].name.lower()]
                except KeyError:
                    pass
        elif companies[key].expires < 0 and companies[key].prospects[0] == "BANKRUPT":
            if randint (0,3) == 0:
                companies[key].__init__(companies[key].name)

        else:
            delta = companies[key].get_value(time) - companies[key].get_value(time-0.2) 
            if delta < 0:
                direction = 'down'
            else:
                direction = 'up'

            companies[key].prospects = [direction,round(abs(delta),2)]

    await bot.process_commands(message)
       
bot.run('NjM2MjIwNDMyNTc5ODIxNTc5.Xa8ejQ.bTTVm7mSgzaHL0nNRM3CYUSwmVk')
