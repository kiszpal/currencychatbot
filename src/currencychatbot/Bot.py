# This example requires the 'message_content' intent.
import os
import dotenv


class Bot:
    '''
    This class represents the currencychatbot client wich is communicating with discord API.
    '''

    # A bot kódjának alapjait https://github.com/indently/discord_bot_python repo alapján valósítottam meg.
    def __init__(self):
        dotenv.load_dotenv()
        self._PRIVATE_TRIGGER = os.getenv("PRIVATE_TRIGGER")
        self._PUBLIC_TRIGGER = os.getenv("PUBLIC_TRIGGER")
        self._TOKEN = os.getenv('DISCORD_TOKEN')
        self._validtriggers = os.getenv("VALID_TRIGGERS")

    @property
    def TOKEN(self):
        return self._TOKEN

    @property
    def validtriggers(self):
        return self._validtriggers

    @property
    def public_trigger(self):
        return self._PUBLIC_TRIGGER

    @public_trigger.setter
    def public_trigger(self, character):
        self._PUBLIC_TRIGGER = character

    @property
    def private_trigger(self):
        return self._PRIVATE_TRIGGER

    @private_trigger.setter
    def private_trigger(self, character):
        self._PRIVATE_TRIGGER = character

    def update_private_trigger(self, character):
        if character in self.validtriggers and character is not self.public_trigger and len(character) == 1 and isinstance(character, str):
            self._PRIVATE_TRIGGER = character
            dotenv.set_key(".env", "PRIVATE_TRIGGER", character)

            return True
        else:
            raise ValueError(f'You tried to set the private trigger to an invalid value. '
                             f'It is either already used by the public trigger wich is <{self.public_trigger}> '
                             f'or it is not a valid character to be used as trigger. Valid triggers: "{self.validtriggers}"')

    def update_public_trigger(self, character):
        if character in self.validtriggers \
                and character is not self.private_trigger \
                and len(character) == 1 and isinstance(character, str):
            self._PUBLIC_TRIGGER = character
            dotenv.set_key(".env", "PUBLIC_TRIGGER", character)

            return True
        else:
            raise ValueError(f'You tried to set the public trigger to an invalid value. '
                             f'It is either already used by the private trigger wich is '
                             f'<{self.private_trigger}> or it is not a valid character to '
                             f'be used as trigger. Valid triggers: "{self.validtriggers}"')
