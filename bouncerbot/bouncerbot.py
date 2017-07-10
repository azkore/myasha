# coding=utf-8
from bot import Bot


class BouncerBot(Bot):
    def __init__(self, config):
        super().__init__(config['bot'])

    def report(self, message):
        replied = self.get_replied_message(message)
        print("Reporting %s" % replied)
        self.delete_message(replied.to_id.channel_id, replied.id)

    spam = report
