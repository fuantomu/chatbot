from twitchAPI.twitch import Twitch


class Client:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.twitch = None

    async def connect(self):
        self.twitch = await Twitch(self.client_id, self.client_secret)
