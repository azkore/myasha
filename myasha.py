# coding=utf-8

import configparser
import time

from bouncerbot import BouncerBot

CONFIG = 'myasha.ini'


def read_config(file):
    """Read config section from file"""
    config = configparser.ConfigParser()
    config.read(file)
    return config


def run():
    config = read_config(CONFIG)

    BouncerBot(config)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    run()
