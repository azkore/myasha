# coding=utf-8
import yaml

from heraldbot import HeraldBot

CONFIG = 'config.yaml'


def read_config(filename):
    with open(filename, 'r') as file:
        config = yaml.load(file)
    return config


def run():
    config = read_config(CONFIG)

    HeraldBot(config)


if __name__ == "__main__":
    run()
