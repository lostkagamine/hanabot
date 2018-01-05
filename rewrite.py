import discord # dee.py
import inspect
import traceback
import sys
import json
from chatterbot import ChatBot
ai = ChatBot('Hana', database='database.db', trainer='chatterbot.trainers.ListTrainer')

# Hana command framework
# (c) ry00001 2018


class InvalidCommand(Exception):
    pass # exception for stuff

class Context:
    'Generic context class to pass to commands.'
    def __init__(self, bot, cmd, message, args):
        self.author = message.author
        self.message = message
        self.channel = message.channel
        self.args = args
        self.invoked_by = cmd
        self.bot = bot

    async def send(self, msg:str, **kwargs):
        await self.channel.send(msg, **kwargs)

class Command:
    'Generic command class to run commands from.'
    def __init__(self, func, **kwargs):
        self.name = kwargs.name if hasattr(kwargs, 'name') else func.__name__
        self.description = kwargs.desc if hasattr(kwargs, 'desc') else None
        self.invoke = func # set the caller to this


class Hana(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cfg = json.load(open('config.json'))
        self.prefix = self.cfg.get('prefix')
        # self.prefix += [f'<@{self.user.id}> ', f'<@!{self.user.id}> ']
        self.commands = {}
        self.event_listeners = {}

    async def on_message(self, msg):
        if msg.content.startswith(tuple(self.prefix)): # hacce
            for i in self.prefix:
                if msg.content.startswith(i):
                    current_prefix = i
            print(current_prefix)
            print(len(current_prefix))
            cmd = msg.content[len(current_prefix):].split(' ')[0]
            args = msg.content[len(current_prefix):].split(' ')[1:]
            print(f'{cmd}, {args}')
            print(self.commands)
            await self.process_commands(msg, cmd, args)

    async def process_commands(self, msg, cmd, args):
        if cmd not in self.commands.keys():
            raise InvalidCommand()
        try:
            await self.commands[cmd].invoke(Context(self, cmd, msg, args))
        except Exception as e:
            await self.dispatch('command_error', e)
        
    async def on_ready(self):
        print('Hana ready!')
             
    def command(self, **kwargs):
        def func_wrapper(func):
            print('it ran')
            self.add_command(func, **kwargs)
        return func_wrapper

    def add_command(self, function, **kwargs):
        if not hasattr(kwargs, 'name'):
            name = function.__name__
        else:
            name = kwargs['name']
        self.commands[name] = Command(function, name=name, desc=kwargs['description'] if hasattr(kwargs, 'description') else None)

hana = Hana()

@hana.command()
async def ping(ctx):
    await ctx.send('Pong.')

hana.run(hana.cfg['token'])
