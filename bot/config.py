import configparser

config = configparser.ConfigParser()
config.read('config.ini')

try:
    list_of_existing_variables = {
        config['DISCORD']['TOKEN'],
        config['DISCORD']['OWNER_ID'],
        config['DISCORD']['NOTIFY_NEW_VERSIONS'],
        config['DISCORD']['IDLE_TIMEOUT'],
        config['MESSAGES']['PREFIX'],
        config['SPOTIFY']['ENABLED'],
        config['SPOTIFY']['ID'],
        config['SPOTIFY']['SECRET'],
    }
except KeyError as e:
    print(f"Your config file is invalid you are missing:\n{e.args[0]}\nCheck example_config.ini to see what it does and add it!")
    exit(1)
