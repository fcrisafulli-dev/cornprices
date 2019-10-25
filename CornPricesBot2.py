import discord
from discord.ext import commands
import pickle
from random import randint
from numpy import sin,cos,mean
import datetime

c_file = 'company.p'
u_file = 'user.p'

bot = commands.Bot(command_prefix='!')
no_portfolio_err = discord.Embed(title="One Sec!", description="You are not registered in the database! \
        Type !register to get startes.", color=0xff0000)
bankrupt_err = discord.Embed(title="Sorry!", description="That company made some poor business decisions and is bankrupt!"\
        , color=0xff0000)
no_shares_err = discord.Embed(title="Sorry!", description="That company has no shares for sale", color=0xff0000)
not_enough_shares_c_err = discord.Embed(title="Sorry!", description="You are trying to buy more shares than that company has!", color=0xff0000)
not_enough_money_err = discord.Embed(title="Bruh, you broke.", description="Not enough money", color=0xff0000)
no_c_err = discord.Embed(title="One Sec!", description="That company does not exist.", color=0xff0000)
not_enough_shares_c_err = discord.Embed(title="You dont own enough shares", color=0xff0000)
no_shares_in_c_err = discord.Embed(title="Oops!",description="You dont own any shares in that company", color=0xff0000)

class Company:
    def __init__(self,name,rem=False):
        self.name = name.lower()
        self.dname = name
        self.offset = randint(1,20)
        self.angle = randint(1,25)
        self.violence = randint(4,9)
        self.rang = randint(5,20)
        self.shares = 3003
        self.bankrupt = False
        self.expires = (self.angle/2)
        self.prospects = ['Starting Anew',0]
        self.tt = 0 #time passed
        self.rem = rem
    def get_prev_value(self,d):
        v = (sin((6.28/self.angle)*(self.tt-d)) * self.rang) + sin((self.violence * (self.tt-d)) + self.offset) \
                * 10 * self.bankrupt
        return round(abs(v+1),2)

    def get_value(self):
        v = (sin((6.28/self.angle)*self.tt) * self.rang) + sin((self.violence * self.tt) + self.offset) * 10 \
                * self.bankrupt
        return round(abs(v+1),2)

class Portfolio:
    def __init__(self,user):
        self.user = user
        #stores shares owned, not in market
        self.shares = {}

        #stores shares in market
        # key: companyname value [#of shares, price]
        self.selling = {}
        self.money = 500

try:
    companies = pickle.load(open(c_file, 'rb'))
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
    portfolios = pickle.load(open(u_file, 'rb'))
except FileNotFoundError:
    portfolios = {}

def save_game():
    pickle.dump( companies, open( c_file , "wb" ) )
    pickle.dump( portfolios, open( u_file , "wb" ) )

def not_registered(user):
    if user in portfolios:
        return False
    else:
        return True

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

!buy companyname ammount -> Buys shares (use 'all' for ammount to buy max)

!sell companyname ammount -> Sells shares back to the company(use 'all' for ammount to sell max)

!sellmarket companyname ammount price -> sell your shares on the user market

!sellmarket companyname @username -> buy shares from a user 

!pay ammount @username -> give money to a user

!shares -> Shows Your Portfolio

!market -> Shows the user market

!moneytop -> Shows leaderboard

!cornprices -> Gets CORN PRICES
""")

@bot.command()
async def register(ctx):
    if str(ctx.message.author) in portfolios:
        await ctx.send(embed=discord.Embed(title="Failed", \
                description=f"{ctx.message.author.name} is already registered",color = 0xff0000))
    else:
        author = ctx.message.author
        portfolios[str(author)] = Portfolio(author.name)
        await ctx.send(embed=discord.Embed(title="Welcome!",\
                description=f"{ctx.message.author.name}, your account has been created. Type !cornhelp to start.", \
                color = 0x00ff00))

@bot.command()
async def cornprices(ctx):
    global time
    prices = discord.Embed(title=f"Corn Prices, from {ctx.message.author.name}", \
            description="!cornhelp for more / updated every 30 seconds", color=0xffff00)

    for key in companies.keys():
        company = companies[key]
        val = company.get_value()
        sh = company.shares
        prices.add_field(name=company.dname, \
                value=f" ${val} | {company.prospects[0]} {company.prospects[1]} | Shares Avaliable: {sh}", inline=False)

    await ctx.message.delete()
    mssg = await ctx.send(embed=prices)
    await mssg.delete(delay=30)

@bot.command()
async def moneytop(ctx):
    M = {}
    i = 0
    for key in portfolios.keys():
        M[key] = portfolios[key].money
        if i >= 8:
            break
        i += 1
    s = sorted(M,key=M.get,reverse=True)
    m = discord.Embed(title="Corntop",description=f"Top 8",color=0x0000ff)
    for key in s:
        m.add_field(name=key,value=f"${round(portfolios[key].money,2)}",inline=False)
    await ctx.message.author.send(embed=m)
    return


@bot.command()
async def pay(ctx, amnt: int, *arg ):
    topay = str(ctx.message.mentions[0])
    if amnt < 1:
        m = discord.Embed(title="Transaction",description=f"Transaction failed: less than 1",color=0xff0000)
        await ctx.send(embed=m)
        return

    if portfolios[str(ctx.message.author)].money >= amnt:
        portfolios[str(ctx.message.author)].money -= amnt
        portfolios[topay].money += amnt
        m = discord.Embed(title="Transaction",description=f"{ctx.message.author.name} payed {topay} ${amnt}",color=0x00ff00)
    else:
        m = discord.Embed(title="Transaction",description=f"Transaction failed: Not enough money",color=0xff0000)
    await ctx.send(embed=m)
    return

@bot.command()
async def shares(ctx):
    user = str(ctx.message.author)
    if not_registered(user):
        await ctx.send(embed=no_portfolio_err) 
        return

    shares = discord.Embed(title=f"{ctx.author.name}'s Shares", description="#Shares", color=0xff9900)
    for key in companies.keys():
        company = companies[key]
        if company.name.lower() in portfolios[user].shares:
            percent = (portfolios[user].shares[company.name] / 3003) * 100
            shares.add_field(name=company.name, value=f"{portfolios[user].shares[company.name]} | {round(percent,2)}% ",\
                    inline=False)
    await ctx.send(embed=shares)

@bot.command()
async def rip_me(ctx):
    del portfolios[str(ctx.message.author)]
    print("Deleted")

@bot.command()
async def money(ctx):
    try:
        cash = portfolios[str(ctx.message.author)].money
        money = discord.Embed(title=f"{ctx.author.name}'s Cash", description=f"${round(cash,2)}", color=0xff0000)
        await ctx.message.delete()
        await ctx.send(embed=money)
    except KeyError:
        await ctx.send(f"{ctx.message.author.name} {no_portfolio_err}" ) 

@bot.command()
async def cornbug(ctx):
    if str(ctx.message.author) != "Fez#1086":
        await ctx.author.send(ctx.message.author)
        return

    d = discord.Embed(title=f"Debug", color=0xffffff)
    for key in companies.keys():
        company = companies[key]
        dt = (((company.expires/.001)*15)/60)/60
        d.add_field(name=f"{company.dname}",value=f"Shares {company.shares}, expires in {dt} hours gt: ({company.angle}), peak {company.rang}, violence {company.violence}, user: {company.rem}",inline=False)
    await ctx.author.send(embed=d)

@bot.command()
async def create(ctx,name):
    if str(ctx.message.author) not in portfolios:
        await ctx.send(f"{ctx.message.author.name} {no_portfolio_err}" ) 
        return
    if portfolios[str(ctx.message.author)].money >= 100000:
        portfolios[str(ctx.message.author)].money -= 100000
        companies[name.lower()] = Company(name,rem=True)
        m = discord.Embed(title=name, description= f"Created by: {ctx.message.author.name}", color=0xff00ff)
        await ctx.send(embed=m)
    else:
        m = discord.Embed(title="Create Failed ($100000 needed)", description= f"{ctx.message.author.name}, bruh you broke.", color=0xff00ff)
        await ctx.send(embed=m)

@bot.command()
async def market(ctx):
    market = discord.Embed(title="User Market",description="User,company,ammount,price")

    for iuser in portfolios.keys():
        user = portfolios[iuser]
        if len(user.selling) <= 0:
            continue

        market.add_field(name=iuser,value="listings:",inline=False)
        for ilisting in user.selling.keys():
            market.add_field(name=ilisting,value=f"#{user.selling[ilisting][0]} / ${user.selling[ilisting][1]}",inline=False)
    m = await ctx.send(embed=market)
    await m.delete(delay=60)

@bot.command()
async def retract(ctx,c: str):
    company = c.lower()
    user = str(ctx.message.author)

    if not_registered(user):
        await ctx.send(embed=no_portfolio_err)
        return
    user = portfolios[user]

    if company in user.selling:
        user.shares[company] += user.selling[company][0]
        del user.selling[company]
        await ctx.send(embed=discord.Embed(title=f"Retracted",description=f"{ctx.message.author.name} retracted their listing in {company}",color=0x0000ff))
        return
    
    else:
        await ctx.send(embed=discord.Embed(title="Retract Failed",description=f"You are not selling any shares in {company}"))    
        return

@bot.command()
async def sellmarket(ctx, c, a, p: int):
    company = c.lower()
    buyer = str(ctx.message.author)

    if not_registered(buyer):
        await ctx.send(embed=no_portfolio_err)
        return

    if company in companies:
        company = companies[company]

        if company.bankrupt:
            await ctx.send(embed=bankrupt_err)
            return
        
        if company.name not in portfolios[buyer].shares:
            await ctx.send(embed=no_shares_in_c_err)

        try: 
            amnt = int(a)
        except ValueError:
            amnt = portfolios[buyer].shares[company.name]

        if amnt <= 0:
            await ctx.send(embed=no_negatives_err)
            return

        if company.name in portfolios[buyer].selling:
            await ctx.send(embed=discord.Embed(title="Already Selling",\
                    description=f"You are already selling shares in that company, use !retract {company.name}",\
                    color = 0xff0000))
            return



        price = p
        portfolios[buyer].selling[company.name] = [amnt,price] 
        portfolios[buyer].shares[company.name] -= amnt

        transaction = discord.Embed(title=f"{ctx.message.author.name}", \
                description=f"Is selling {amnt} shares of {company.dname} for ${round(price,2)}", color=0x00ff00)
        await ctx.message.delete()
        await ctx.send(embed=transaction)
        return

    else:
        await ctx.send(embed=no_c_err)
        return

@bot.command()
async def buymarket(ctx, c: str, *arg):
    tobuy = str(ctx.message.mentions[0])
    company = c.lower()
    buyer = str(ctx.message.author)

    if not_registered(buyer):
        await ctx.send(embed=no_portfolio_err)
        return

    if company in companies:
        company = companies[company]

        if company.bankrupt:
            await ctx.send(embed=bankrupt_err)
            return
        
        if company.name not in portfolios[tobuy].selling:
            await ctx.send(embed=discord.Embed(title="Not selling",description=f"{tobuy} is not selling any shares in {company.dname}"))

        amnt = portfolios[tobuy].selling[company.name][0] 
        price = portfolios[tobuy].selling[company.name][1] 

        if price > portfolios[buyer].money:
            await ctx.send(embed=not_enough_money_err)
            return

        portfolios[buyer].money -= price
        portfolios[tobuy].money += price

        if company.name in portfolios[buyer].shares:
            portfolios[buyer].shares[company.name] += amnt
        else:
            portfolios[buyer].shares[company.name] = amnt

        del portfolios[tobuy].selling[company.name]

        transaction = discord.Embed(title=f"{ctx.message.author.name}", \
                description=f"Bought {tobuy}'s listing of {company.dname} shares for ${round(price,2)}", color=0xff0000)
        await ctx.message.delete()
        await ctx.send(embed=transaction)
        return

    else:
        await ctx.send(embed=no_c_err)
        return

@bot.command()
async def buy(ctx, c, a):
    company = c.lower()
    buyer = str(ctx.message.author)

    if not_registered(buyer):
        await ctx.send(embed=no_portfolio_err)
        return

    if company in companies:
        company = companies[company]

        if company.bankrupt:
            await ctx.send(embed=bankrupt_err)
            return
        
        if company.shares <= 0:
            await ctx.send(embed=no_shares_err)
            return

        try: 
            amnt = int(a)
        except ValueError:
            amnt = portfolios[buyer].money // company.get_value()

        if amnt > company.shares:
            await ctx.send(embed=not_enough_shares_c_err)
            return

        price = amnt * company.get_value()

        if price > portfolios[buyer].money:
            await ctx.send(embed=not_enough_money_err)
            return

        portfolios[buyer].money -= price
        company.shares -= amnt

        if company.name in portfolios[buyer].shares:
            portfolios[buyer].shares[company.name] += amnt
        else:
            portfolios[buyer].shares[company.name] = amnt

        transaction = discord.Embed(title=f"{ctx.message.author.name}", \
                description=f"Bought {amnt} shares from {company.name} for ${round(price,2)}", color=0xff0000)
        await ctx.message.delete()
        await ctx.send(embed=transaction)
        return

    else:
        await ctx.send(embed=no_c_err)
        return

@bot.command()
async def sell(ctx, c, a):
    company = c.lower()
    buyer = str(ctx.message.author)

    if not_registered(buyer):
        await ctx.send(embed=no_portfolio_err)
        return

    if company in companies:
        company = companies[company]

        if company.bankrupt:
            await ctx.send(embed=bankrupt_err)
            return
        
        
        if company.name not in portfolios[buyer].shares:
            await ctx.send(embed=no_shares_in_c_err)

        try: 
            amnt = int(a)
        except ValueError:
            amnt = portfolios[buyer].shares[company.name]

        if amnt <= 0:
            await ctx.send(embed=no_negative_err)
            return

        price = amnt * company.get_value()

        portfolios[buyer].money += price
        company.shares += amnt
        portfolios[buyer].shares[company.name] -= amnt

        transaction = discord.Embed(title=f"{ctx.message.author.name}", \
                description=f"Sold {amnt} shares to {company.name} for ${round(price,2)}", color=0xff0000)
        await ctx.message.delete()
        await ctx.send(embed=transaction)
        return

    else:
        await ctx.send(embed=no_c_err)
        return

@bot.event
async def on_message(message):
    global time
    global atime

    #if message.author == bot.user:
    #    return

    now = datetime.datetime.now()
    #time delta
    td = (now - atime).seconds 

    if td > 30: #seconds
        save_game()
        atime = datetime.datetime.now()
    try:
        #compnay time delta
        ctd = (td // 30) * .004
        #time += mtd
    except:
        print("Time Set to .5")
        ctd = 0
        #time = .5
    for key in companies.keys():
        company = companies[key]
        company.expires -= ctd
        company.tt += ctd
        if company.expires < 0 and not company.bankrupt: 
            company.bankrupt = True
            for key2 in portfolios.keys():
                try:
                    del portfolios[key2].shares[company.name]
                    del portfolios[key2].selling[company.name]
                except KeyError:
                    pass

        elif company.bankrupt:
            if company.rem == True:
                del companies[key]
                continue

            if company.tt < 3:
                company.__init__(company.name)

        else:
            #price delta
            pdelta = company.get_value() - company.get_prev_value(0.004) 
            if pdelta < 0:
                direction = 'down'
            else:
                direction = 'up'

            company.prospects = [direction,round(abs(pdelta),2)]

    await bot.process_commands(message)
       
bot.run('NjM2MjIwNDMyNTc5ODIxNTc5.XbLXfw.6WObmTmpfbvhoJRTIYAOPf0dFf4')
