from programy.clients.embed.basic import EmbeddedBasicBot
from programy.clients.embed.datafile import EmbeddedDataFileBot

files = {'aiml': ['y-bot/storage/categories'] }

my_bot = EmbeddedDataFileBot(files, defaults=True)

print("Response = %s" % my_bot.ask_question("Hello"))