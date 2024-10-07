import configparser

config = configparser.ConfigParser()
config.read('bot\example_config.ini')

REQUIRED_CONFIG = {
                'DISCORD': ['TOKEN', 'OWNER_ID', 'NOTIFY_NEW_VERSIONS', 'IDLE_TIMOUT'],
                'MESSAGES': ['PREFIX'],
                'SPOTIFY': ['ENABLED', 'ID', 'SECRET']
                }

def check_config_values(sections: dict = REQUIRED_CONFIG):

    missing_options = []
    for section in sections:
        for option in sections[section]:
            if not config.has_option(section, option):
                missing_options.append(option)

    return missing_options
