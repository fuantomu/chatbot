from twitchAPI.type import ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage, ChatSub, ChatCommand

from src.database.dictionary import Entry, Dictionary
from src.database.quote import Quote, QuoteDatabase
from src.logger.log import get_logger
from datetime import datetime

QUOTE_DB = QuoteDatabase("data/quotes.json")
DICTIONARY_DB = Dictionary("data/entries.json")


class ChatClient:
    log = get_logger("ChatClient")

    def __init__(self, twitch_client, channel: str):
        self.twitch_client = twitch_client
        self.channel = channel
        self.chat = None

    async def connect(self):
        self.log.info("Connecting to Twitch chat")
        self.chat = await Chat(self.twitch_client)
        self.chat.register_event(ChatEvent.READY, self.on_ready)
        self.chat.register_event(ChatEvent.MESSAGE, self.on_message)
        self.chat.register_event(ChatEvent.SUB, self.on_sub)
        self.chat.register_command("help", self.help_command)
        self.chat.register_command("quote", self.quote_command)
        self.chat.register_command("setquote", self.setquote_command)
        self.chat.register_command("reloadquotes", self.reload_quotes)
        self.chat.register_command("dictionemsy", self.entry_command)
        self.chat.register_command("setdict", self.setentry_command)
        self.chat.register_command("reloaddict", self.reload_entries)

    def start(self):
        if self.chat.is_connected():
            raise Exception("Chat client is already connected")
        self.chat.start()

    def stop(self):
        if not self.chat:
            raise Exception("Chat client is not connected")
        self.chat.stop()
        self.chat = None

    async def on_ready(self, ready_event: EventData):
        self.log.info("Bot is ready for work, joining channels")
        await ready_event.chat.join_room(self.channel)

    async def on_message(self, msg: ChatMessage):
        self.log.debug(f"in {msg.room.name}, {msg.user.name} said: {msg.text}")

    async def on_sub(self, sub: ChatSub):
        self.log.debug(
            f"New subscription in {sub.room.name}:\\n"
            f"  Type: {sub.sub_plan}\\n"
            f"  Message: {sub.sub_message}"
        )

    async def help_command(self, cmd: ChatCommand):
        if len(cmd.parameter) == 0:
            await cmd.reply("you did not tell me what to reply with")
        else:
            match cmd.parameter.lower():
                case "quote":
                    await cmd.reply(
                        "quote command: !quote - get a random quote from the bot's quote database"
                    )
                case "setquote":
                    await cmd.reply(
                        "setquote command: !setquote <user:> <quote> - add a new quote in the bot's quote database"
                    )
                case "dictionemsy":
                    await cmd.reply(
                        "dictionemsy command: !dictionemsy <optional:word> - get the definition of a word from the bot's dictionemsy"
                    )
                case "setdict":
                    await cmd.reply(
                        "setdict command: !setdict <word> <text> - add a new entry to the bot's dictionemsy"
                    )
                case "setquote":
                    await cmd.reply(
                        "setquote command: !setquote <user:> <quote> - add a new quote in the bot's quote database"
                    )
                case _:
                    await cmd.reply(f"Invalid help option '{cmd.parameter.lower()}'")

    async def quote_command(self, cmd: ChatCommand):
        quote = QUOTE_DB.get_random_quote()
        if quote is None:
            return await cmd.reply("No quotes in the database yet")
        if isinstance(quote.date, str):
            await cmd.reply(
                f'"{quote.text}" - {quote.user if quote.user else "emsbaems"}, {quote.date}'
            )
        else:
            await cmd.reply(
                f'"{quote.text}" - {quote.user if quote.user else "emsbaems"}, {datetime.fromtimestamp(quote.date / 1000).year}'
            )

    async def setquote_command(self, cmd: ChatCommand):
        if len(cmd.parameter) == 0:
            await cmd.reply("Missing quote text, use !setquote <user:> <quote>")
        if ":" not in cmd.parameter:
            QUOTE_DB.add_quote(
                Quote(
                    text=cmd.parameter,
                    author=cmd.user.name,
                    date=cmd.sent_timestamp,
                    user=None,
                )
            )
        else:
            user, quote_text = cmd.parameter.split(":", 1)
            QUOTE_DB.add_quote(
                Quote(
                    text=quote_text.lstrip(),
                    author=cmd.user.name,
                    date=cmd.sent_timestamp,
                    user=user.strip(),
                )
            )
        return await cmd.reply("Quote added to the database")

    async def reload_quotes(self, cmd: ChatCommand):
        QUOTE_DB.load_quotes()
        return await cmd.reply("Quotes reloaded")

    async def entry_command(self, cmd: ChatCommand):
        entry = DICTIONARY_DB.get_random_entry()
        if len(DICTIONARY_DB.entries) == 0:
            return await cmd.reply("No entries in the dictionemsy yet")

        if len(cmd.parameter) == 0:
            entry = DICTIONARY_DB.get_random_entry()
        else:
            entry = DICTIONARY_DB.get_entry(cmd.parameter)
            if entry is None:
                return await cmd.reply(f'No entry found for "{cmd.parameter}"')
        return await cmd.reply(f'"{entry.word}" - {entry.text}')

    async def setentry_command(self, cmd: ChatCommand):
        if len(cmd.parameter.split()) <= 1:
            return await cmd.reply(
                "Missing entry word or text, use !setentry <word> <text>"
            )
        if DICTIONARY_DB.get_entry(cmd.parameter.split()[0]) is not None:
            return await cmd.reply(
                f'An entry for "{cmd.parameter.split()[0]}" already exists in the dictionemsy'
            )
        DICTIONARY_DB.add_entry(
            Entry(
                word=cmd.parameter.split()[0].capitalize(),
                text=" ".join(cmd.parameter.split()[1:]),
                author=cmd.user.name,
                date=cmd.sent_timestamp,
            )
        )
        return await cmd.reply(
            f'Entry for "{cmd.parameter.split()[0].capitalize()}" added to the dictionemsy'
        )

    async def reload_entries(self, cmd: ChatCommand):
        DICTIONARY_DB.load_entries()
        return await cmd.reply("Dictionemsy entries reloaded")
