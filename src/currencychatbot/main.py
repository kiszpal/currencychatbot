from currencychatbot import Bot
import discord
from src.currencychatbot.response import Response, ResponseArguments

if __name__ == '__main__':
    bot = Bot()
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    response = None
    args = ResponseArguments()

    @client.event
    async def on_ready():

        print(f'We have logged in as {client.user}!')

    @client.event
    async def on_message(message):
        if message.author != client.user and (message.content[0] == bot.public_trigger or message.content[0] == bot.private_trigger):
            response = Response(message, bot, args)
            history = [message async for message in message.channel.history(limit=10)]

            return_value = response.process_message(history)

            if isinstance(return_value, discord.File):
                if response.is_private:
                    await message.author.send(file=return_value)
                else:
                    await message.channel.send(file=return_value)
            else:
                if response.is_private:
                    await message.author.send(return_value)
                else:
                    await message.channel.send(return_value)

    client.run(bot.TOKEN)
