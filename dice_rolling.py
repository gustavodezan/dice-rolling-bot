# rolls dice and sends motivational messages along with the results
#----------------------------------------------------------------------

import discord
import random
import frases
import operator

client = discord.Client()

@client.event
async def on_ready():
    print('online'.format(client))
    
# ------------
# Constantes
# ------------
ops = {
    '+' : operator.add,
    '-' : operator.sub,
    '*' : operator.mul,
    '/' : operator.truediv,
    '%' : operator.mod,
    '^' : operator.xor,
}

#Dice rolls
def RollDice(dice):
    return random.randrange(1,(dice+1))

sig = '~'

#Dice roll system
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    frase_escolhida = frases.motivacionais[random.randrange(0,len(frases.motivacionais))]

    user_request = message.author.id
    mention = ('<'+'@'+str(message.author.id)+'>')

    dices = message.content
    dices = dices.split()
    dice_pool = []
    total = mod = changed1s = reroll =  0
    mod_op = operator.add

    # -------------
    # Dice Rolling
    # -------------
    # Needs to be optimized
    
    #Normal roll -> it's the first part of any roll
    if message.content.startswith(f'{sig}r'):
        await message.channel.send(f'{mention}\n__{frase_escolhida}__',tts = False)
        number,dice = dices[1].split('d')
        for operation in ops:
            if operation in dice:
                mod_op = ops[operation]
                dice,mod = dice.split(operation)
                mod = int(mod)

        number,dice = int(number),int(dice)
        for die in range(number):
            new_die = RollDice(dice)
            dice_pool.append(new_die)

        for die in dice_pool:
            total += die
        result = str(dice_pool).strip('[]')
        if message.content.startswith(f'{sig}rr'):
          for die in dice_pool:
            await message.channel.send(f'1d{dice} ({die}) + {mod} = {mod_op(die,mod)}')
        await message.channel.send(f'**Result**: {dices[1]} ({result})')
        old_pool = len(dice_pool)

    #Great-weapon master -> reroll any dice <= limit
    if message.content.startswith(f'{sig}rgw'):
        min_v = int(dices[-1])
        i = 0
        while i < old_pool:
            if dice_pool[i] <= min_v:
                reroll = True
                await message.channel.send(f'Reroll {dice_pool[i]}')
                dice_pool.pop(i)
                new_die = RollDice(dice)
                dice_pool.insert(i,new_die)
                
            i += 1

    #Elemental Adept -> increase by 1 any dice <= limit
    elif message.content.startswith(f'{sig}rel'):
        min_v = int(dices[-1])
        i = 0
        while i < len(dice_pool):
            if dice_pool[i] < min_v:
                changed1s += 1
                dice_pool[i] = min_v
            i+=1

    #HP Roll -> if 1s are rolled -> (1 + reroll)/2
    elif message.content.startswith(f'{sig}rhm'):
        min_v = int(dices[-1])
        i = 0
        while i < old_pool:
            if dice_pool[i] <= min_v:
                reroll = True
                new_die = RollDice(dice)
                new_die = int((new_die + dice_pool[i])/2)
                await message.channel.send(f'Reroll {dice_pool[i]}')
                dice_pool.pop(i)
                dice_pool.insert(i,new_die)
            i += 1

    #Help
    elif message.content.startswith(f'{sig}help'):
        await message.channel.send('Help:\n> ~r XdY: normal roll\n> ~rgw XdY m: great-weapon master. m = min value.\n> ~rel XdY m: elemental adept. m = min value\n> ~rhm XdY m: (roll <= m) -> (roll + reroll)/2\n> ~adv/dis x (DC)\n*~pontos é fake*')

    # Probabilidade de sucesso - calcula a probabilidade de sucesso em um teste com vantagem ou desvantagem
    # Vantagem
    if message.content.startswith(f'{sig}adv'):
        s = message.content
        result = (2*int(dices[-1])-1)/400
        if dices[1] == '<':
            result = 0
            i = 0
            while i < (int(dices[-1])):
                result += (2*(int(dices[2])-i)-1)/400
                i+=1
        elif dices[1] == '>':
            result = 0
            i = 0
            while i < (21-int(dices[-1])):
                result += (2*(int(dices[2])+i)-1)/400
                i+=1
        result = '{0:.2f}'.format(result*100)
        await message.channel.send(f'Probabilidade de rolar {s[5:]}: {result}%')  
    # Desvantagem
    elif message.content.startswith(f'{sig}dis'):
        s = message.content
        dic_roll = {'1':20,'2':19,'3':18,'4':17,'5':16,'6':15,'7':14,'8':13,'9':12,'10':11,'11':10,'12':9,'13':8,'14':7,'15':6,'16':5,'17':4,'18':3,'19':2,'20':1}
        result = (2*dic_roll[dices[-1]]-1)/400
        if dices[1] == '<':
            result = 0
            i = 0
            while i < (int(dices[-1])):
                result += (2*dic_roll[str(int(dices[-1])-i)]-1)/400
                i += 1
        elif dices[1] == '>':
            result = 0
            i = 0
            while i < (21-int(dices[-1])):
                result += (2*dic_roll[str(int(dices[-1])+i)]-1)/400
                i+=1
        result = '{0:.2f}'.format(result*100)
        await message.channel.send(f'Probabilidade de rolar {s[5:]}: {result}%')

    # send message
    if message.content.startswith(f'{sig}r'):
        if reroll == True or changed1s > 0:
            total = 0                     
            for dado in dice_pool:
                total = total+dado

            result = str(dice_pool).strip('[]')
            await message.channel.send(f'**Result**: ({result})')
        await message.channel.send(f'**Total** = {mod_op(total,mod)}')
    
    if message.content.startswith(f'-rapq'):
        await message.channel.send(frases.rap_r,tts = True)

client.run('TOKEN')
