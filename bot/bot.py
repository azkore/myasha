# coding=utf-8
from telethon import TelegramClient
from telethon.tl.functions.channels import (
    DeleteMessagesRequest,
    GetMessagesRequest
)
from telethon.tl.types import (
    InputPeerChannel,
    UpdateEditChannelMessage,
    UpdateNewChannelMessage,
    UpdatesTg
)


class Bot(TelegramClient):
    def __init__(self, config):
        super().__init__(config['session'],
                         config['api_id'],
                         config['api_hash'])
        self.login(config['phone'])
        self.channels = self.init_channels(config['channel_ids'].split(','))
        self.add_update_handler(self.update_handler)

    def login(self, phone):
        self.connect()
        if not self.is_user_authorized():
            self.send_code_request(phone)
            self.sign_in(phone, input('Enter code: '))

    def init_channels(self, ids):
        entities = self.get_dialogs(limit=0)[1]
        return {e.id: InputPeerChannel(e.id, e.access_hash)
                for e in entities if str(e.id) in ids}

    def in_watched_channels(self, message):
        return message.to_id.channel_id in self.channels

    @staticmethod
    def update_contains_message(update):
        return isinstance(update, (UpdateNewChannelMessage,
                                   UpdateEditChannelMessage))

    @staticmethod
    def is_forwarded(message):
        return message.fwd_from

    def get_fresh_messages(self, update):
        return [u.message for u in update.updates
                if self.update_contains_message(u)
                and self.in_watched_channels(u.message)
                and not self.is_forwarded(u.message)]

    def delete_message(self, channel_id, message_id):
        return self(
            DeleteMessagesRequest(self.channels[channel_id], [message_id])
        )

    def get_message(self, channel_id, message_id):
        return self(
            GetMessagesRequest(self.channels[channel_id], [message_id])
        ).messages[0]

    def get_replied_message(self, message):
        return self.get_message(message.to_id.channel_id,
                                message.reply_to_msg_id)

    def execute(self, message):
        command = message.message[1:]
        try:
            getattr(self, command)(message)
        except (AttributeError, TypeError):
            pass

    def update_handler(self, update):
        if isinstance(update, UpdatesTg):
            for message in self.get_fresh_messages(update):
                if message.message.startswith('/'):
                    self.execute(message)
