import argparse
import asyncio

from src.client.chat import ChatClient
from src.client.client import Client

parser = argparse.ArgumentParser(description="Configure the chatbot")
parser.add_argument(
    "--env-file", help="Path to the environment file", default=".env.local"
)
parser.add_argument("--autorun", help="Autorun", action="store_true")

MENU = """
1.  Connect Twitch Client
2.  Authenticate with Twitch
3.  Refresh OAUTH Token

4.  Connect Chat Client

5.  Start Chat Client

99. Exit
"""

if __name__ == "__main__":
    from src.config.config import Config

    args = parser.parse_args()

    config = Config(env_file=args.env_file)
    client = Client(config.client_id, config.client_secret)
    chat_client = None
    loop = asyncio.new_event_loop()

    if args.autorun:
        loop.run_until_complete(client.connect())
        loop.run_until_complete(config.authenticate(client.twitch))
        chat_client = ChatClient(client.twitch, config.target_channel)
        loop.run_until_complete(chat_client.connect())
        chat_client.start()
    else:
        answer = True
        while answer is not None:
            print(MENU)
            try:
                ans = input("Select an option: ")
                if ans == "1":
                    print("")
                    loop.run_until_complete(client.connect())
                    print("")
                elif ans == "99":
                    print("Exiting...")
                    break
                elif client.twitch:
                    if ans == "2":
                        print("")
                        loop.run_until_complete(config.authenticate(client.twitch))
                        print("")
                    elif ans == "3":
                        print("")
                        loop.run_until_complete(config.refresh_oauth())
                        print("")
                    elif ans == "4":
                        print("")
                        chat_client = ChatClient(client.twitch, config.target_channel)
                        loop.run_until_complete(chat_client.connect())
                        print("")
                    elif ans == "5" and chat_client:
                        print("")
                        chat_client.start()
                        print("")
                    else:
                        print("Invalid choice, try again")
                else:
                    print("Invalid choice, try again")
            except KeyboardInterrupt:
                print("Exiting...")
                if client.twitch:
                    chat_client.stop()
                    chat_client = ChatClient(client.twitch, config.target_channel)
                    loop.run_until_complete(chat_client.connect())
