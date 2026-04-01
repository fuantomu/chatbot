import json
from random import choice


class Quote:
    def __init__(self, text: str, author: str, date: float, user: str = None):
        self.text = text
        self.author = author
        self.date = date
        self.user = user


class QuoteDatabase:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.quotes = self.load_quotes()

    def load_quotes(self):
        with open("data/quotes.json", "r") as f:
            data = json.load(f)
            quotes = []
            for quote_data in data:
                quote = Quote(
                    text=quote_data["text"],
                    author=quote_data["author"],
                    date=quote_data["date"],
                    user=quote_data.get("user"),
                )
                quotes.append(quote)
            return quotes

    def save_quotes(self):
        with open("data/quotes.json", "w") as f:
            json.dump([quote.__dict__ for quote in self.quotes], f)

    def add_quote(self, quote: Quote):
        self.quotes.append(quote)
        self.save_quotes()

    def get_random_quote(self) -> Quote:
        if len(self.quotes) == 0:
            return None
        return choice(self.quotes)
