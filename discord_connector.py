# This example requires the 'members' privileged intents

import discord
from discord.ext import commands
import random
import string
from game import mafia as m

colors = {
    'civilian': 0xeb4034,
    'mafia': 0x000000,
    'detective': 0xedbd2b,
    'boss': 0x5e2358
}

avail_roles = ['boss', 'detective', 'mafia']

rolecount = {
}

def make_code():
    result = ''
    for i in range(6):
        result += random.choice(string.ascii_uppercase+string.digits)   
    return result

modes = {
    'Классика': discord.Colour.dark_red(),
    'Обычная игра': discord.Colour.dark_blue(),
    'Бар "Последний кон"': discord.Colour.dark_magenta()
}

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.group()
async def mafia(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Напишите /mafia shuffle, чтобы распределить номера.')

@mafia.command(name='shuffle')
async def _shuffle(ctx):
    roommaker_role = discord.utils.find(lambda r: r.name == 'Ведущий', ctx.guild.roles)
    if roommaker_role in ctx.author.roles:
        if not ctx.author.voice:
            await ctx.send('**Для начала игры вам необходимо присодениться к голосовому каналу.**')
        else:
            players = ctx.author.voice.channel.members
            players = [a for a in ctx.author.voice.channel.members if discord.utils.find(
                lambda r: r.name == 'Игрок', ctx.guild.roles) in a.roles]
            if ctx.author in players:
                players.remove(ctx.author)
            numbersPool = list(range(1, len(players)+1))
            random.shuffle(numbersPool)

            authorname = ctx.author.display_name
            if ' ' in authorname:
                name_temp = authorname.split(' ')
                if any(char.isdigit() for char in name_temp[0]):
                    authorname = ' '.join(name_temp[1:])
                    try:
                        await ctx.author.edit(nick=authorname)
                    except discord.Forbidden:
                        await ctx.send(f'Не могу переименовать <@{ctx.author.id}> - нет прав.')
                    

            for num, player in enumerate(players):
                name = player.display_name
                if ' ' in name:
                    name_temp = name.split(' ')
                    if any(char.isdigit() for char in name_temp[0]):
                        name = ' '.join(name_temp[1:])
                if numbersPool[num] > 9:
                    numbersPool[num] = 'a' + str(numbersPool[num])
                new = str(numbersPool[num]) + '. ' + name
                try:
                    await player.edit(nick=new)
                except discord.Forbidden:
                    await ctx.send(f'Не могу переименовать <@{player.id}> — **номер {numbersPool[num]}**')
            await ctx.send('**Номера успешно установлены!**')
    else:
        await ctx.send('**Вы не являетесь ведущим!**')

@mafia.command(name='clear', usage='Убрать все номера.')
async def _clear(ctx):
    roommaker_role = discord.utils.find(
        lambda r: r.name == 'Ведущий', ctx.guild.roles)
    if roommaker_role in ctx.author.roles:
        if not ctx.author.voice:
            await ctx.send('**Для начала игры вам необходимо присодениться к голосовому каналу.**')
        else:
            players = ctx.author.voice.channel.members

            for player in players:
                name = player.display_name
                if ' ' in name:
                    name_temp = name.split(' ')
                    if any(char.isdigit() for char in name_temp[0]):
                        name = ' '.join(name_temp[1:])
                        try:
                            await player.edit(nick=name)
                        except discord.Forbidden:
                            await ctx.send(f'**Не могу переименовать <@{player.id}>**')

            await ctx.send('**Номера успешно сняты!**')
    else:
        await ctx.send('**Вы не являетесь ведущим!**')


@mafia.command(name='clearall', usage='Убрать все номера.')
async def _clearall(ctx):
    roommaker_role = discord.utils.find(
        lambda r: r.name == 'Ведущий', ctx.guild.roles)
    if roommaker_role in ctx.author.roles:
        players = ctx.guild.members

        for player in players:
            name = player.display_name
            if ' ' in name:
                name_temp = name.split(' ')
                if any(char.isdigit() for char in name_temp[0]):
                    name = ' '.join(name_temp[1:])
                    try:
                        await player.edit(nick=name)
                    except discord.Forbidden:
                        await ctx.send(f'**Не могу переименовать <@{player.id}>**')

        await ctx.send('**Номера успешно сняты!**')
    else:
        await ctx.send('**Вы не являетесь ведущим!**')
   
@mafia.command(name='role')
async def _roleset(ctx, name: str=None, amount: int=None):
    global rolecount

    if not name or name not in avail_roles:
        await ctx.send('Неизвестная роль!')
    else:
        if amount == 0:
            del rolecount[name]
        else:
            rolecount[name] = amount
        await ctx.send(f'Для {name} установлено количество игроков {amount}.')

@mafia.command(name='start', usage='Раздать роли.')
async def _start(ctx):
    if ctx.author.voice:
        game = m.Game()
        mplayers = [a for a in ctx.author.voice.channel.members if discord.utils.find(
            lambda r: r.name == 'Игрок', ctx.guild.roles) in a.roles]

        if ctx.author in mplayers:
            mplayers.remove(ctx.author)
        for d_user in mplayers:
            game.addPlayer(m.Player(d_user.id, d_user.display_name))

        global rolecount
        for role in rolecount:
            try:
                game.setRole(role, rolecount[role])
            except Exception:
                await ctx.send(f'Недостаточно игроков для введения роли {role}.')

        if game.size < game.minPlayers:
            await ctx.send(f'Недостаточно игроков! Минимум: {game.minPlayers}')
        else:
            game.assignRoles()
            info = '\n====================\n**Роли игроков:**'
            
            for player in game.players:
                role = player.role.display_name
                discord_user = ctx.guild.get_member(player.id)

                embedVar = discord.Embed(title=f"Ваша роль: {role}.", color=colors[player.role.name])

                await discord_user.send(embed=embedVar)

                info += f"\n {discord_user.display_name} > {player.role.display_name}"
                
            await ctx.author.send(info)
    else:
        await ctx.send('**Подключитесь к голосовому каналу!**')

bot.run('token')
