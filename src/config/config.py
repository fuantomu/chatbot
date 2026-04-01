from dotenv import load_dotenv, set_key
import os

import requests
from twitchAPI.oauth import UserAuthenticator, refresh_access_token
from twitchAPI.type import AuthScope

SCOPES = [
    AuthScope.CHANNEL_BOT,
    AuthScope.CHANNEL_READ_POLLS,
    AuthScope.CHANNEL_MANAGE_POLLS,
    AuthScope.CHANNEL_READ_PREDICTIONS,
    AuthScope.CHANNEL_MANAGE_PREDICTIONS,
    AuthScope.CHANNEL_MANAGE_RAIDS,
    AuthScope.CHANNEL_READ_REDEMPTIONS,
    AuthScope.CHANNEL_MANAGE_REDEMPTIONS,
    AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
    AuthScope.CHANNEL_READ_VIPS,
    AuthScope.CHANNEL_MANAGE_VIPS,
    AuthScope.MODERATOR_MANAGE_ANNOUNCEMENTS,
    AuthScope.USER_BOT,
    AuthScope.USER_READ_CHAT,
    AuthScope.USER_WRITE_CHAT,
    AuthScope.CHAT_EDIT,
    AuthScope.CHAT_READ,
]

TWITCH_OAUTH_VALIDATE_URL = "https://id.twitch.tv/oauth2/validate"


class Config:

    def __init__(self, env_file=".env"):

        load_dotenv(env_file)
        self.client_id = os.environ.get("CLIENT_ID")
        if not self.client_id:
            self.logger.warning("CLIENT_ID is not set")
        self.client_secret = os.environ.get("CLIENT_SECRET")
        if not self.client_secret:
            self.logger.warning("CLIENT_SECRET is not set")
        self.target_channel = os.environ.get("TARGET_CHANNEL")
        if not self.target_channel:
            self.logger.warning("TARGET_CHANNEL is not set")
        self.oauth_token = os.environ.get("OAUTH_TOKEN")
        self.refresh_token = os.environ.get("OAUTH_REFRESH_TOKEN")

    async def authenticate(self, twitch):
        if self.oauth_token and self.refresh_token:
            await twitch.set_user_authentication(
                self.oauth_token, SCOPES, self.refresh_token
            )
            return
        auth = UserAuthenticator(twitch, SCOPES, force_verify=False)
        self.oauth_token, self.refresh_token = await auth.authenticate()
        await twitch.set_user_authentication(
            self.oauth_token, SCOPES, self.refresh_token
        )
        set_key(".env.local", "OAUTH_TOKEN", self.oauth_token)
        set_key(".env.local", "OAUTH_REFRESH_TOKEN", self.refresh_token)

    async def refresh_oauth(self):
        self.oauth_token, self.refresh_token = await refresh_access_token(
            self.refresh_token, self.client_id, self.client_secret
        )
        set_key(".env.local", "OAUTH_TOKEN", self.oauth_token)
        set_key(".env.local", "OAUTH_REFRESH_TOKEN", self.refresh_token)

    async def verify_auth(self, oauth_token: str) -> bool:
        headers = {"Authorization": f"OAuth {oauth_token}"}
        request = requests.get(TWITCH_OAUTH_VALIDATE_URL, headers=headers)
        return request.status_code == 200
