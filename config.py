from configparser import ConfigParser

file = "config.ini"

config = ConfigParser()

read = config.read(file)


def read_config(section, element):
    b = config[section][element]
    return b
