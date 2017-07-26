# coding=utf-8
import datetime
import time

from bot import Bot


class HeraldBot(Bot):
    def __init__(self, config):
        super().__init__(config['bot'])
        self.config = config['heraldbot']
        self.interval = self.config['interval']
        # TODO: ensure serialization of events to free memory
        self.init_events()
        print(self.last_event_ids)
        self.loop()

    def init_events(self):
        self.events = {channel_id: self.get_admin_log(channel).events
                       for channel_id, channel in self.channels.items()}
        self.last_event_ids = {
            channel_id: self.get_last_event_id(self.events[channel_id])
            for channel_id in self.channels
        }

    @staticmethod
    def get_last_event_id(events):
        return max([e.id for e in events]) if events else 0

    def loop(self):
        while True:
            self.last_called = datetime.datetime.now()
            time.sleep(self.interval)
            for channel in self.channels.values():
                self.monitor(channel)

    def monitor(self, channel):
        log = self.get_admin_log(channel,
                                 min_id=self.last_event_ids[channel.id] + 1)
        if log is None:
            return
        if log.events:
            self.events[channel.id].extend(log.events)
            self.last_event_ids[channel.id] = max(e.id for e in log.events)
        for event in log.events:
            user = next(u for u in log.users if event.user_id == u.id)
            action_name = type(event.action).__name__.replace(
                'ChannelAdminLogEventAction', '')
            message = "{} {} {}".format(event.date,
                                        self.get_name(user),
                                        action_name)
            if action_name == "DeleteMessage":
                message += " '{}'".format(event.action.message.message)
            if action_name == 'EditMessage':
                old = event.action.prev_message.message
                new = event.action.new_message.message
                message += (": '{}' -> '{}'").format(old, new)

            self.send_message(channel, message)
