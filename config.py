from configparser import ConfigParser

file = "config.ini"
config = ConfigParser()
config.read(file)
env = config['env']['env']
conf_file = 'config.' + env + '.ini'
conf = ConfigParser()
conf.read(conf_file)


def read(section, element):
    b = conf[section][element]
    return b
