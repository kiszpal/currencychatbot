import os

from Currency import Currency


class InvalidChangeError(Exception):
    def __init__(self, bot):
        self.message = f"You can only set a new trigger character either for " \
                       f"private or public trigger if you use the current **public** " \
                       f"trigger which is <**{bot.public_trigger}**> and you are not in private chat with me."
        super().__init__(self.message)


class CollidingTriggerError(Exception):
    def __init__(self, new_trigger_type, new_trigger, bot):
        self.message = f"The new trigger collides with an existing trigger.\n" \
                       f"You tried to change the {new_trigger_type} trigger to <**{new_trigger}**>, " \
                       f"but it is already in use.\n" \
                       f"Current public trigger: <**{bot.public_trigger}**>.\n" \
                       f"Current private trigger: <**{bot.private_trigger}**>."
        super().__init__(self.message)


class BaseResponse:
    def __init__(self, bot_client):
        self._response = f"Did not understand what you said, " \
                         f"for more information about how I work " \
                         f"please type in {bot_client.public_trigger}help " \
                         f"to have me respond here or {bot_client.private_trigger}help " \
                         f"to respond for you in private chat."

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, new_response):
        self._response = new_response


class ResponseArguments:
    def __init__(self):
        self._action = None
        self._amount = None
        self._desired = None
        self._base = None
        self._days = None
        self._plot = False

    def reset(self):
        self._action = None
        self._amount = None
        self._desired = None
        self._base = None
        self._days = None
        self._plot = False

    @property
    def plot(self):
        return self._plot

    def set_plot(self, is_plot):
        self._plot = is_plot

    @property
    def action(self):
        return self._action

    def set_action(self, action):
        self._action = action

    @property
    def amount(self):
        return self._amount

    def set_amount(self, amount):
        self._amount = amount

    @property
    def desired(self):
        return self._desired

    def set_desired(self, desired):
        self._desired = desired

    @property
    def base(self):
        return self._base

    def set_base(self, base):
        self._base = base

    @property
    def days(self):
        return self._days

    def set_days(self, days):
        self._days = days


class Response(BaseResponse):
    def __init__(self, msg, bot_client, arguments: ResponseArguments):
        super().__init__(bot_client)
        self._bot_client = bot_client
        self._message = msg
        self._trigger = self.message.content[0]
        self._keyword = self.message.content[1:].split(" ")[0].lower()
        self._u_message = self.message.content[len(self.keyword) + 2:].lower()
        self._type_help = f"\nPlease see help by typing {bot_client.private_trigger}help " \
                          f"to get help message in private chat or {bot_client.public_trigger}help " \
                          f"to get help message here!"
        self._is_private = \
            True if self.trigger == bot_client.private_trigger else False if self.trigger == bot_client.public_trigger else None
        self._arguments = arguments

    @property
    def args(self):
        return self._arguments

    def reset_args(self):
        self.args.reset()

    @property
    def is_private(self):
        return self._is_private

    @property
    def bot(self):
        return self._bot_client

    @property
    def type_help(self):
        return self._type_help

    @property
    def message(self):
        return self._message

    @property
    def trigger(self):
        return self._trigger

    @property
    def u_message(self):
        return self._u_message

    @property
    def keyword(self):
        return self._keyword

    def is_update_private(self, change_type):
        match change_type:
            case "private":
                return True
            case "public":
                return False
            case _:
                # TODO
                raise NotImplementedError("Make a new help response for when change is used wrong")

    def process_change(self):

        if self.is_private:
            raise InvalidChangeError(self.bot)

        new_trigger = self.u_message[-1]

        update_private = self.is_update_private(self.keyword.split("_")[1])

        if new_trigger == self.bot.public_trigger or new_trigger == self.bot.private_trigger:
            raise CollidingTriggerError("private" if update_private else "public", new_trigger, self.bot)

        if update_private:
            prev_trigger = self.bot.private_trigger
            self.bot.update_private_trigger(new_trigger)
        else:
            prev_trigger = self.bot.public_trigger
            self.bot.update_public_trigger(new_trigger)
        return f'Successfully updated {"private" if update_private else "public"} trigger ' \
               f'from <**{prev_trigger}**> to <**{new_trigger}**>'

    def is_last_keyword(self, word, history):
        found_latest = False
        for hist_msg in history:
            if hist_msg.author.bot:
                continue
            if not found_latest:
                found_latest = True
                continue
            if hist_msg.content.split(" ")[0][1:].lower() == word:
                return True
            return False

    def process_message(self, history=None):
        try:
            match self.keyword.split("_")[0]:
                case "help":
                    return os.getenv("HELP")

                case "change":
                    self.process_change()

                case "currency":
                    return f"You can use the following commands to get information from me about currencies:\n" \
                           f"exchange:\n" \
                           f"   usage: <trigger>exchange <Base currency>\n" \
                           f"       After that,you will be able to tell me the amount, then the desired currency.\n" \
                           f"rate:\n" \
                           f"   usage: <trigger>rate <Base currency>\n" \
                           f"       After that,you will be able to tell me the desired currencies.\n" \
                           f"       You can give only one currency if you want.\n" \
                           f"historical:\n" \
                           f"   usage: <trigger>historical <currency1,currency2,...>\n" \
                           f"       After that, I will ask for the currency you want to compare to, then the interval in days.\n" \
                           f"       You can give only one currency if you want.\n" \
                           f'Be careful, actions regarding to currencies are only available when used in the correct order!.\n' \
                           f'For more information type <{self.bot.public_trigger}>help or <{self.bot.private_trigger}>help.' \

                case "exchange":
                    if self.is_last_keyword("currency", history):
                        self.reset_args()
                        self.args.set_action("exchange")
                        if len(self.u_message) != 3:
                            return "Currency declarations are always 3 characters long!"
                        self.args.set_base(self.u_message.upper())
                        return "Give me the desired currency using: <trigger>amount <number>"

                    self.reset_args()

                case "amount":
                    if self.args.action == "exchange":
                        if int(self.u_message) < 0:
                            return "Give me a positive number!"
                        self.args.set_amount(self.u_message)
                        return "Give me your desired currency to change to, using: <trigger>desired <currency>"

                    self.reset_args()

                case "desired":
                    desired = list()
                    for i, curr in enumerate(self.u_message.split(",")):
                        if len(curr) != 3:
                            return "Currency declarations are always 3 characters long!"
                        desired.append(curr.upper())
                    self.args.set_desired(desired)
                    match self.args.action:
                        case "exchange":
                            product = Currency().change(self.args.base, self.args.desired, self.args.amount)
                            ret_msg = f'{self.args.amount} {self.args.base} is worth {product} {self.args.desired[0]}.'
                            self.reset_args()

                            return ret_msg

                        case "rate":
                            product = Currency().get_curr_rates(self.args.base, self.args.desired)
                            self.reset_args()

                            return product

                        case "historical":
                            product = Currency().historical_rates(self.args.base, self.args.desired, self.args.days, self.args.plot)
                            self.reset_args()

                            return product

                case "rate":
                    if self.is_last_keyword("currency", history):
                        self.reset_args()
                        self.args.set_action("rate")
                        if len(self.u_message) != 3:
                            return "Currency declarations are always 3 characters long!"
                        self.args.set_base(self.u_message.upper())
                        return "Give me the desired currency using: <trigger>desired <currency>"

                    self.reset_args()

                case "historical":
                    if self.is_last_keyword("currency", history):
                        self.reset_args()
                        self.args.set_action("historical")
                        bases = self.u_message.split(",")
                        for i, currency in enumerate(bases):
                            if len(currency) != 3:
                                return "Currency declarations are always 3 characters long!"
                            bases[i] = bases[i].upper()

                        self.args.set_base(bases)
                        return "Give me the number of days using: <trigger>days <number_of_days>"

                    self.reset_args()

                case "days":
                    if self.args.action == "historical":
                        if int(self.u_message) <= 0:
                            return "Give me a positive number!"
                        self.args.set_days(self.u_message)
                        return "Do you wish to get the information on a plot?\n" \
                               "Usage: <trigger>plot <yes|no>"

                    self.reset_args()

                case "plot":
                    if self.args.action == "historical":
                        if self.u_message == "yes":
                            self.args.set_plot(True)
                        elif self.u_message == "no":
                            self.args.set_plot(False)
                        else:
                            return "You gave me wrong input. Valid inputs: <yes|no>."
                        return "Give me the desired currency using: <trigger>desired <currency(ies)>"

                    self.reset_args()

                case "triggers":
                    return f'Private trigger: "{self.bot.private_trigger}"\n' \
                           f'Public trigger: "{self.bot.public_trigger}"\n' \
                           f'Valid triggers: "{os.getenv("VALID_TRIGGERS")}"'

                case _:
                    return self.response

        except (ValueError, InvalidChangeError, CollidingTriggerError) as e:
            return str(e)
