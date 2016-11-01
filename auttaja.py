#!/usr/bin/env python3.5

import asyncio
import discord
import re
import sys
from logbook import Logger, StreamHandler, RotatingFileHandler, NestedSetup
from pluginbase import PluginBase

plugin_base = PluginBase(package='auttaja.plugins')
plugin_source = plugin_base.make_plugin_source(
        searchpath=['./plugins'])

class BotCmd():
    def __init__(self, cmd, callback, permlevel):
        self.cmd = cmd
        self.callback = callback
        self.permlevel = permlevel

    def Call(self, cmd, message, app, args=None):
        logger.info("Calling callback!")
        self.callback(cmd, args, message, app)

class Application():

    def __init__(self, dclient, logger):
        self.plugins = dict()
        self.commands = dict()
        self.classes = list()
        self.dclient = dclient
        self.logger = logger
    
    def setup(self):
        self.logger.info('Setting up bot and plugins')
        self.callbacks = dict()
        self.plugins = dict()

        self.logger.info("Available plugins: {}".format(plugin_source.list_plugins()))
        for plugin_name in plugin_source.list_plugins():
            self.plugins[plugin_name] = plugin_source.load_plugin(plugin_name)
            self.plugins[plugin_name].setup(self, self.dclient, self.logger)

    def register_callback(self, callback_name, function):
        if not callback_name in self.callbacks:
            self.callbacks[callback_name] = list()
        self.callbacks[callback_name].append(function)

    def register_command(self, name, callback, permlevel=1):
        new_cmd = BotCmd(name, callback, permlevel)
        self.commands[name] = new_cmd
        logger.info(new_cmd.cmd)
        logger.info(new_cmd.callback)
        logger.info(new_cmd.permlevel)

    def reload(self):
        # Reloads plugins
        pass

    def enable(self, plugin_name):
        # Enable a specific plugin
        pass

    def disable(self, plugin_name):
        # Disable a specific plugin
        pass
    def send_pm(self, user, msg):
        asyncio.run_coroutine_threadsafe(self.dclient.start_private_message(user), self.dclient.loop)
        asyncio.run_coroutine_threadsafe(self.dclient.send_message(user, msg), self.dclient.loop)

    def reply(self, channel, msg):
        asyncio.run_coroutine_threadsafe(self.dclient.send_message(channel, msg), self.dclient.loop)

StreamHandler(sys.stdout).push_application()
#RotatingFileHandler('logs/auttaja.log', mode='a+').push_application()

logger = Logger('auttaja')
dclient = discord.Client()
app = Application(dclient, logger)

def main():
    app.setup()
    app.dclient.run('mykey')

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

@dclient.event
async def on_resumed(message):
    if currentFuncName() in app.callbacks:
        for callback in app.callbacks[currentFuncName()]:
            try:
                callback(message, app)
            except Exception as e:
                logger.error(e)

@dclient.event
async def on_error(event, *args, **kwargs):
    if currentFuncName() in app.callbacks:
        for callback in app.callbacks[currentFuncName()]:
            try:
                callback(event, args, kwargs, app)
            except Exception as e:
                logger.error(e)

@dclient.event
async def on_message(message):
    if not message.author.bot:
        recmp = re.compile("^-[A-za-z]+.*")
        if not recmp.match(message.content) == None:
        #if message.content.startswith('-'):
            logger.info("Command executed by: {}: {}".format(message.author.name, message.content))
            splitmsg = message.content.split(' ')
            cmd = splitmsg[0].strip('-')
            logger.info("Command base found: {}".format(cmd))
            if cmd in app.commands:
                logger.info("Command exists, running plugin")
                args = splitmsg[1:]
                app.commands[cmd].Call(cmd, message, app, args)
            else:
                logger.info("Command doesn't exist")
                app.reply(message.channel, "```Unknown command```")

        if currentFuncName() in app.callbacks:
            for callback in app.callbacks[currentFuncName()]:
                try:
                    callback(message, app)
                except Exception as e:
                    logger.error(e)

@dclient.event
async def on_socket_raw_receive(msg):
    if currentFuncName() in app.callbacks:
        for callback in app.callbacks[currentFuncName()]:
            try:
                callback(msg, app)
            except Exception as e:
                logger.error(e)

@dclient.event
async def on_socket_raw_send(msg):
    if currentFuncName() in app.callbacks:
        for callback in app.callbacks[currentFuncName()]:
            try:
                callback(msg, app)
            except Exception as e:
                logger.error(e)

@dclient.event
async def on_message_delete(message):
    if currentFuncName() in app.callbacks:
        for callback in app.callbacks[currentFuncName()]:
            try:
                callback(message, app)
            except Exception as e:
                logger.error(e)

@dclient.event
async def on_message_edit(before, after):
    if currentFuncName() in app.callbacks:
        for callback in app.callbacks[currentFuncName()]:
            try:
                callback(before, after, app)
            except Exception as e:
                logger.error(e)

if __name__ == '__main__':
    main()
