#!/usr/bin/env python
# -*- coding: utf-8 -*-
#pylint: disable=locally-disabled

"""
    Telegram bot that sends a voice message with a game voice line.
    Author: Cauã Martins Pessoa <caua539@gmail.com>
"""

import json
import logging

from uuid import uuid4
from telegram import InlineQueryResultAudio
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from telegram.ext.dispatcher import run_async

import GameVoicesFinder

RESPONSE_DICT = {}

# Enable logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(__name__)

# Load config file
with open('config.json') as config_file:
    CONFIGURATION = json.load(config_file)


def start_command(bot, update):
    """ Handle the /start command. """
    bot.sendMessage(update.message.chat_id, text='Hi, my name is @gamevoicesbot, I can send'
                                                 ' you voice messages with some games voice lines, use'
                                                 ' the command\n/help to see how to use me.')

def help_command(bot, update):
    """ Handle the /help command. """
    bot.sendMessage(update.message.chat_id,
                    text='Usage: \nYou don\'t need to add me to a group, I\' an inline bot.\n\n'
                         'Write \'@gamevoicesbot CHARACTER/VOICE LINE\' in chat to get a voice '
                         'line in return, then just click it to send it.\n'
                         'Example: \'@gamevoicesbot Pudge/Get Over Here\'\n\n'
                         'Note that there\'s no need to use the full name of the character or pack.'
                         'Characters/pack with two or more names should be separated with underlines.\n'
                         'Ex: phantom_assassin.\n\n'
                         'Current games:\n'
                         '- Dota 2 (all characters, all voice lines)\n'
                         '- Overwatch (only 3 voice lines, work in progress)\n'
                         '- Some easter eggs ;)\n')

@run_async
def response_inline(bot, update):
    """
        Handle inline queries

        The user sends a message with a desired game voice line and the bot sends a voice
        message with the best voice line.
    """
                
    
    message = update.inline_query.query
    user = update.inline_query.from_user.first_name
    specific_hero = None
    
    if message.find("/") >= 0:
        specific_hero, query = message.split("/")
        specific_hero.strip()
        query.strip()
    else:
        query = message
        query.strip()
        
    LOGGER.info("New query from: %s %s\nQuery: %s",
                update.inline_query.from_user.first_name,
                update.inline_query.from_user.last_name,
                update.inline_query.query)

    hero, responses = GameVoicesFinder.prepare_responses(query, RESPONSE_DICT, specific_hero)
    
    results = list()
    if not hero or not responses:
        pass
    else:
        for i in range(len(responses)):
            heroname = hero[i].replace('_responses', '')
            sresult = InlineQueryResultAudio(id = uuid4(),
                                             audio_url = responses[i]["url"],
                                             title="""{}""".format(responses[i]["text"]),
                                             performer= heroname)
            results.append(sresult)
        bot.answerInlineQuery(update.inline_query.id, results=results)

def error_handler(bot, update, error):
    """ Handle polling errors. """
    LOGGER.warn('Update "%s" caused error "%s"', str(update), str(error))


def main():
    """ Main """
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(CONFIGURATION["telegram_token"])

    global RESPONSE_DICT
    # Load the responses
    RESPONSE_DICT = GameVoicesFinder.load_response_json(CONFIGURATION["responses_file"])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_handler(InlineQueryHandler(response_inline))
    dp.add_handler(CommandHandler("help", help_command))

    # log all errors
    dp.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()