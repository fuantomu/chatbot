import json
from random import choice


class Entry:
    def __init__(self, word: str, text: str, author: str, date: float):
        self.word = word
        self.text = text
        self.author = author
        self.date = date


class Dictionary:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.entries = self.load_entries()

    def load_entries(self):
        with open("data/dictionary.json", "r") as f:
            data = json.load(f)
            entries = []
            for entry_data in data:
                entry = Entry(
                    word=entry_data["word"],
                    text=entry_data["text"],
                    author=entry_data["author"],
                    date=entry_data["date"],
                )
                entries.append(entry)
            return entries

    def save_entry(self):
        with open("data/dictionary.json", "w") as f:
            json.dump([entry.__dict__ for entry in self.entries], f)

    def add_entry(self, entry: Entry):
        self.entries.append(entry)
        self.save_entry()

    def get_random_entry(self) -> Entry:
        if len(self.entries) == 0:
            return None
        return choice(self.entries)

    def get_entry(self, word: str) -> Entry:
        for entry in self.entries:
            if entry.word.lower() == word.lower():
                return entry
        return None
