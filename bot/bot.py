# coding=utf-8
from telethon import TelegramClient
from telethon.tl.functions.channels import (
    DeleteMessagesRequest,
    GetMessagesRequest
)
from telethon.tl.types import (
    UpdatesTg
)


class Bot(TelegramClient):
    def __init__(self, config):
        super().__init__(config['session'],
                         config['api_id'],
                         config['api_hash'])
        self.login(config['phone'])
        self.channels = self.init_channels(config['channel_ids'])
        self.add_update_handler(self.update_handler)

    def login(self, phone):
        self.connect()
        if not self.is_user_authorized():
            self.send_code_request(phone)
            self.sign_in(phone, input('Enter code: '))

    def init_channels(self, ids):
        entities = self.get_dialogs(limit=0)[1]
        return {e.id: e for e in entities if e.id in ids}

    def in_watched_channels(self, message):
        return message.to_id.channel_id in self.channels

    @staticmethod
    def update_contains_text_message(update):
        try:
            if update.message.message:
                return True
        except AttributeError:
            return False

    @staticmethod
    def is_forwarded(message):
        try:
            message.fwd_from
        except AttributeError:
            pass

    @staticmethod
    def is_reply(message):
        return message.reply_to_msg_id

    def get_fresh_text_messages(self, update):
        return [u.message for u in update.updates
                if self.update_contains_text_message(u)
                and self.in_watched_channels(u.message)
                and not self.is_forwarded(u.message)]

    def delete_message(self, channel_id, message_id):
        request = DeleteMessagesRequest(
            self.channels[channel_id], [message_id]
        )
        return self(request)

    def get_message(self, channel_id, message_id):
        request = GetMessagesRequest(self.channels[channel_id], [message_id])
        return self(request).messages[0]

    def get_replied_message(self, message):
        return self.get_message(message.to_id.channel_id,
                                message.reply_to_msg_id)

    def execute(self, message):
        try:
            cmd_function = getattr(self, 'cmd_' + message.message[1:])
        except AttributeError:
            pass
        else:
            cmd_function(message)

    def update_handler(self, update):
        if isinstance(update, UpdatesTg):
            for message in self.get_fresh_text_messages(update):
                if message.message.startswith('/'):
                    self.execute(message)
