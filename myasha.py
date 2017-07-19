# coding=utf-8

import time

import yaml

from bouncerbot import BouncerBot

CONFIG = 'config.yaml'


def read_config(filename):
    with open(filename, 'r') as file:
        config = yaml.load(file)
    return config


def run():
    config = read_config(CONFIG)

    BouncerBot(config)
    while True:
        time.sleep(1)


if __name__ == "__main__":
    run()
