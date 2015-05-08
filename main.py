import hangups
import hangups.auth

import asyncio
import logging
import sys, os
import appdirs
import json

import handler
import util

logger = logging.getLogger(__name__)

CONFIG = json.load(open("config.json"))

BOTNAME = CONFIG["name"]

class ChatMessage(object):
    def __init__(self, conversation, chat_message):
        self.__conversation = conversation
        self.__chat_message = chat_message

    def conv_id(self):
        return self.__conversation.id_

    def author(self):
        return self.__chat_message.user_id

    def text(self):
        return self.__chat_message.text

    def timestamp(self):
        return self.__chat_message.timestamp

    def reply(self, text):
        segments = hangups.ChatMessageSegment.from_str(text)
        asyncio.async(self.__conversation.send_message(segments))


class Server(object):

    def __init__(self, cookies=None):
        self._hangups = hangups.Client(cookies)
        self._hangups.on_connect.add_observer(self._on_hangups_connect)

    def run(self):
        loop = asyncio.get_event_loop()
        logger.info('Waiting for hangups to connect...')
        loop.run_until_complete(self._hangups.connect())

    # Hangups Callbacks

    def _on_hangups_connect(self, initial_data):
        """Called when hangups successfully auths with hangouts."""
        self._user_list = hangups.UserList(
            self._hangups, initial_data.self_entity, initial_data.entities,
            initial_data.conversation_participants
        )
        self._conv_list = hangups.ConversationList(
            self._hangups, initial_data.conversation_states, self._user_list,
            initial_data.sync_timestamp
        )
        
        self.__id = initial_data.self_entity.id_.gaia_id
        
        self._conv_list.on_event.add_observer(self._on_hangups_event)
        logger.info('Hangups connected. Connect your IRC clients!')

    def _on_hangups_event(self, conv_event):
        """Called when a hangups conversation event occurs."""
        if isinstance(conv_event, hangups.ChatMessageEvent) and conv_event.user_id.gaia_id != self.__id:
            conversation = self._conv_list.get(conv_event.conversation_id)
            self.__parse_message(ChatMessage(conversation, conv_event))
    
    def __parse_message(self, chatmessage):
            logger.info("%s - %s", chatmessage.conv_id(), chatmessage.text())
            message = chatmessage.text().lower()
            message = util.sanitise(message)
            logger.info('"' + message + '"')
            response = None
            if get_message_to_me(message) != None:
                message = get_message_to_me(message)
                logger.info('Message to Me: "' + message + '"')
                response = handler.get_message_to_me(message)
            else:
                response = handler.get_message_to_all(message)
                logger.info(response)
            if response != None:
                logger.info(response)
                chatmessage.reply(response)
            #self.__save_message(chatmessage) # FIXME save disabled for now
            

def get_message_to_me(message):
    if not message.lower().startswith(BOTNAME.lower()):
        logger.info('-> ignored due to nickname')
        return
    message = message[len(BOTNAME):]
    if not message.startswith((':', ',', ' ')):
        logger.info('-> ignored due to punctuation')
        return
    return message[1:].lstrip()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.getLogger('hangups').setLevel(logging.WARNING)
    dirs = appdirs.AppDirs('hangups', 'hangups')
    default_cookies_path = os.path.join(dirs.user_cache_dir, 'cookies.json')
    cookies = hangups.auth.get_auth_stdin(default_cookies_path)
    Server(cookies=cookies).run()