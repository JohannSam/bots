import discord  
import random
import json 
import os 
import asyncio

score=0
player1=""
player2="" 
turn=""
gameOver=True 
board=[]
winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8], 
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]

from discord.ext import commands 

client=commands.Bot(command_prefix="/",intents=discord.Intents.all()) 

mainshop=[{"name":"Watch","price":100,"description":"Time"},{"name":"Laptop","price":1000,"description":"Work"},{"name":"PC","price":10000,"description":"Gaming"}]

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="/theone")) 
    
    await client.change_presence(activity=discord.Game(name="on 100 servers")) 

    print("Bot is ready") 

async def ch_pr():
    await client.wait_until_ready()
    statuses=["/theone","on 100 servers"] 
    while not client.is_closed():
        status=random.choice(statuses)
        await client.change_presence(activity=discord.Game(name=status)) 
        await asyncio.sleep(30)  

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = "Woah, chill bruh, try again in **{:.2f}** seconds.".format(error.retry_after) 
        await ctx.send(msg)  

@client.command()
async def playgame(ctx, p1: discord.Member, p2: discord.Member): 
    global count
    global player1
    global player2
    global turn
    global gameOver

    if gameOver:
        global board
        board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:",
                 ":white_large_square:", ":white_large_square:", ":white_large_square:"]
        turn = ""
        gameOver = False
        count = 0

        player1 = p1
        player2 = p2

        # print the board

        line = ""
        for x in range(len(board)):
            if x == 2 or x == 5 or x == 8:
                line += " " + board[x]
                await ctx.send(line)
                line = ""
            else:
                line += " " + board[x]

        # determine who goes first

        num = random.randint(1, 2)
        if num == 1:
            turn = player1
            await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
        elif num == 2:
            turn = player2
            await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
    else:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")

@client.command()
async def place(ctx, pos: int):
    global turn 
    global player1
    global player2
    global board
    global count
    global gameOver

    if not gameOver:
        mark = ""
        if turn == ctx.author:
            if turn == player1:
                mark = ":regional_indicator_x:"
            elif turn == player2:
                mark = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:" :
                board[pos - 1] = mark
                count += 1

                # print the board

                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winningConditions, mark)
                print(count)
                if gameOver == True:
                    await ctx.send(mark + " wins!")
                elif count >= 9:
                    gameOver = True
                    await ctx.send("It's a tie!")

                # switch turns

                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Be sure to choose an integer between 1 and 9 (inclusive) and an unmarked tile.")
        else:
            await ctx.send("It is not your turn.")
    else:
        await ctx.send("Please start a new game using the /playgame command.")


def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True

@playgame.error 
async def tictactoe_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention 2 players for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping players (ie. <@688534433879556134>).")

@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please enter a position you would like to mark.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to enter an integer.")
 
@client.command()
async def hello(ctx):
    await ctx.send("Sup human") 
@client.command()
async def creatorname(ctx):
    await ctx.send("J. Johann") 
@client.command() 
async def balance(ctx):
    user=ctx.author 
    await open_account(ctx.author)
    users=await get_bank_data() 
    wallet_amt=users[str(user.id)]["wallet"]   
    bank_amt=users[str(user.id)]["bank"] 
    em=discord.Embed(title=f"{ctx.author.name}'s balance",color=discord.Color.blue())  
    em.add_field(name="Wallet balance",value=wallet_amt) 
    em.add_field(name="Bank balance",value=bank_amt)   
    await ctx.send(embed=em)  

@client.command() 
@commands.cooldown(1,10,commands.BucketType.user)
async def beg(ctx):
    user=ctx.author 
    await open_account(ctx.author)
    users=await get_bank_data() 
    earnings=random.randrange(1001)  
    await ctx.send(f"Someone gave you {earnings} coins!!") 
    users[str(user.id)]["wallet"]+=earnings  
    with open("bank.json","w") as f:
        json.dump(users,f) 

@client.command()
async def withdraw(ctx,amount=None):
    await open_account(ctx.author)  
    if amount==None:
        await ctx.send("Please enter the amount.") 
        return 
    bal=await update_bank(ctx.author) 
    amount=int(amount)
    if amount>bal[1]:
        await ctx.send("You don't have much money!")   
        return 
    if amount<0:
        await ctx.send("Amount must be positive!") 
        return 
    await update_bank(ctx.author,amount)   
    await update_bank(ctx.author,-1*amount,"bank")    
    await ctx.send(f"You withdrew {amount} coins!")  

@client.command()
async def deposit(ctx,amount=None): 
    await open_account(ctx.author)  
    if amount==None:
        await ctx.send("Please enter the amount.") 
        return 
    bal=await update_bank(ctx.author) 
    amount=int(amount)
    if amount>bal[0]: 
        await ctx.send("You don't have much money!")   
        return 
    if amount<0:
        await ctx.send("Amount must be positive!") 
        return 
    await update_bank(ctx.author,-1*amount)   
    await update_bank(ctx.author,amount,"bank")    
    await ctx.send(f"You deposited {amount} coins!") 

@client.command()
@commands.cooldown(1,10,commands.BucketType.user)
async def send(ctx,member: discord.Member,amount=None): 
    await open_account(ctx.author) 
    await open_account(member)  
    if amount==None:
        await ctx.send("Please enter the amount.") 
        return 
    bal=await update_bank(ctx.author) 
    amount=int(amount)
    if amount>bal[1]:
        await ctx.send("You don't have much money!")   
        return 
    if amount<0:
        await ctx.send("Amount must be positive!") 
        return 
    await update_bank(ctx.author,-1*amount,"bank")     
    await update_bank(member,amount,"bank")     
    await ctx.send(f"You gave {amount} coins!")    

async def open_account(user):
    users=await get_bank_data() 
    if str(user.id) in users:
        return False 
    else:
        users[str(user.id)] = {} 
        users[str(user.id)]["wallet"]=0 
        users[str(user.id)]["bank"]=0  
    with open("bank.json","w") as f:
        json.dump(users,f) 
    return True  
async def get_bank_data():
    with open("bank.json","r") as f:
        users=json.load(f) 
    return users 

async def update_bank(user,change=0,mode="wallet"):
    users=await get_bank_data()
    users[str(user.id)][mode]+=change  
    with open("bank.json","w") as f: 
        json.dump(users,f) 
    bal=[users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]  
    return bal 

@client.command()
async def shop(ctx):
    em=discord.Embed(title="Shop",color=discord.Color.green()) 
    for item in mainshop:
        name=item["name"] 
        price=item["price"] 
        desc=item["description"] 
        em.add_field(name=name,value=f"${price} | {desc}")     
    await ctx.send(embed=em)  

@client.command()
@commands.cooldown(1,10,commands.BucketType.user)
async def buy(ctx,item,amount=1):
    await open_account(ctx.author) 
    res=await buy_this(ctx.author,item,amount) 
    if not res[0]:
        if res[1]==1:
            await ctx.send("That object isn't there!")
            return 
        if res[1]==2:
            await ctx.send(f"You don't have enough money in your wallet to buy {item}.") 
            return 
    await ctx.send(f"You just bought {amount} {item}.") 

@client.command()
async def bag(ctx):
    await open_account(ctx.author) 
    user=ctx.author
    users=await get_bank_data() 
    try:
        bag=users[str(user.id)]["bag"]
    except:
        bag=[] 
    em=discord.Embed(title="Bag",color=discord.Color.green())
    for item in bag:
        name=str.title(item["item"])        
        amount=item["amount"]  
        em.add_field(name=name,value=amount) 
    await ctx.send(embed=em)     


async def buy_this(user,item_name,amount):
    item_name=item_name.lower() 
    name_=None
    for item in mainshop:
        name=item["name"].lower() 
        if name==item_name:
            name_=name
            price=item["price"]
            break 
    if name_==None:
        return[False,1] 
    cost=price*amount
    users=await get_bank_data() 
    bal=await update_bank(user) 
    if bal[0]<cost:
        return[False,2]
    try:
        index=0
        t=None 
        for thing in users[str(user.id)]["bag"]:
            n=thing["item"] 
            if n==item_name:
                old_amt=thing["amount"] 
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1
        if t==None:
            obj={"item":item_name,"amount":amount} 
            users[str(user.id)]["bag"].append(obj) 
    except:
        obj={"item":item_name,"amount":amount} 
        users[str(user.id)]["bag"]=[obj] 
    with open("bank.json","w") as f:
        json.dump(users,f) 
    await update_bank(user,cost*-1,"wallet") 
    return [True,"Worked"]   


@client.command()
@commands.cooldown(1,10,commands.BucketType.user)
async def sell(ctx,item,amount = 1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author,item,amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That Object isn't there!")
            return
        if res[1]==2:
            await ctx.send(f"You don't have {amount} {item} in your bag.")
            return
        if res[1]==3:
            await ctx.send(f"You don't have {item} in your bag.")
            return

    await ctx.send(f"You just sold {amount} {item}.")


async def sell_this(user,item_name,amount,price = None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price==None:
                price = 0.9* item["price"]
            break

    if name_ == None:
        return [False,1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False,2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index+=1 
        if t == None:
            return [False,3]
    except:
        return [False,3]    

    with open("bank.json","w") as f:
        json.dump(users,f)

    await update_bank(user,cost,"wallet")

    return [True,"Worked"]

@client.command(aliases = ["leaderboard"])
async def lb(ctx,x = 1):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total,reverse=True)    

    em = discord.Embed(title = f"Top {x} Richest People" , description = "This is decided on the basis of raw money in the bank and wallet.",color = discord.Color.red()) 
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = client.get_user(id_)
        name = member.name
        em.add_field(name = f"{index}. {name}" , value = f"{amt}",  inline = False) 
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed = em) 

client.loop.create_task(ch_pr()) 

client.run("TOKEN")    