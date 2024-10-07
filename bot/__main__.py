from bot import *
from config import config as config, check_config_values


def main():
    intents = intents=discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    
    missing_values = check_config_values()
    if len(missing_values) > 0:
        print(f'Missing required options in config file: {missing_values}')
    else:
        TOKEN = config['DISCORD']['TOKEN']
        print(TOKEN)
        Bot(TOKEN, intents)
    
if(__name__ == '__main__'):
    main()
