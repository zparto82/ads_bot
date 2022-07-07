from configparser import ConfigParser


def read_config(section, element):
    file = "config.ini"

    config = ConfigParser()

    read = config.read(file)

    b = config[section][element]

    return b
