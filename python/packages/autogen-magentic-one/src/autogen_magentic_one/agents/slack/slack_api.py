import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Optional, Dict, Any

class SlackAPI:
    def __init__(self):
        """
        Initialize the SlackAPI class.
        Loads environment variables from .env file.
        """
        load_dotenv()
        self.bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.user_token = os.getenv('SLACK_USER_TOKEN')
        
        if not self.bot_token:
            raise ValueError("Error: SLACK_BOT_TOKEN environment variable not set")
        if not self.user_token:
            print("Warning: SLACK_USER_TOKEN environment variable not set. User token functionality will be unavailable.")
        
        self.bot_client = WebClient(token=self.bot_token)
        self.user_client = WebClient(token=self.user_token) if self.user_token else None

    def send_message(self, channel: str, message: str, use_user_token: bool = False) -> Dict[str, Any]:
        print(f"send_message({channel}, {message}, {use_user_token})")
        """
        Send a message to a Slack channel.

        Args:
        channel (str): The name or ID of the Slack channel to send the message to.
        message (str): The message to send.
        use_user_token (bool): If True, use the user token instead of the bot token. Defaults to False.

        Returns:
        Dict[str, Any]: A dictionary containing the result of the operation.
        """
        client = self.user_client if use_user_token and self.user_client else self.bot_client
        
        try:
            # Send the message
            response = client.chat_postMessage(channel=channel, text=message)
            return {"success": response["ok"]}
        except SlackApiError as e:
            return {"error": f"Error sending message: {e}"}

    def send_private_message(self, user_id: str, message: str, use_user_token: bool = False) -> Dict[str, Any]:
        """
        Send a private message to a Slack user.

        Args:
        user_id (str): The ID of the Slack user to send the message to.
        message (str): The message to send.
        use_user_token (bool): If True, use the user token instead of the bot token. Defaults to False.

        Returns:
        Dict[str, Any]: A dictionary containing the result of the operation.
        """
        client = self.user_client if use_user_token and self.user_client else self.bot_client
        
        try:
            # Open a direct message channel with the user
            response = client.conversations_open(channel=user_id)
            if not response["ok"]:
                return {"error": f"Error opening conversation: {response['error']}"}
            
            channel_id = response["channel"]["id"]
            
            # Send the message to the direct message channel
            response = client.chat_postMessage(channel=channel_id, text=message)
            return {"success": response["ok"]}
        except SlackApiError as e:
            return {"error": f"Error sending private message: {e}"}

    def get_unread_messages(self, channel: str, use_user_token: bool = False) -> Dict[str, Any]:
        """
        Get unread messages from a Slack channel.

        Args:
        channel (str): The name or ID of the Slack channel to get messages from.
        use_user_token (bool): If True, use the user token instead of the bot token. Defaults to False.

        Returns:
        Dict[str, Any]: A dictionary containing the unread messages (with sender information) or an error message.
        """
        client = self.user_client if use_user_token and self.user_client else self.bot_client

        try:
            # Get the channel ID if a channel name was provided
            if not channel.startswith('C') and not channel.startswith('D'):
                channel_id = client.conversations_list(types="public_channel,private_channel")
                channel_id = next((c['id'] for c in channel_id['channels'] if c['name'] == channel), None)
                if not channel_id:
                    return {"error": f"Channel '{channel}' not found"}
            else:
                channel_id = channel

            # Get the user's ID
            user_info = client.auth_test()
            user_id = user_info['user_id']

            # Get the last read message timestamp
            channel_info = client.conversations_info(channel=channel_id)
            last_read = channel_info['channel'].get('last_read', '0')

            # Fetch messages
            result = client.conversations_history(channel=channel_id)
            
            # Filter out messages from the current user and include sender information
            unread_messages = []
            for msg in result['messages']:
                if msg['ts'] > last_read and msg.get('user') != user_id:
                    sender_info = client.users_info(user=msg['user'])
                    sender_name = sender_info['user']['real_name']
                    unread_messages.append({
                        'text': msg.get('text', ''),
                        'sender': sender_name
                    })
                elif msg['ts'] <= last_read:
                    # We've reached messages that have been read, so we can stop
                    break

            return {"unread_messages": unread_messages}

        except SlackApiError as e:
            return {"error": f"Error getting unread messages: {e}"}

    def list_channels(self, use_user_token: bool = False) -> Dict[str, Any]:
        """
        List all channels that the bot is a member of.

        Args:
        use_user_token (bool): If True, use the user token instead of the bot token. Defaults to False.

        Returns:
        Dict[str, Any]: A dictionary containing the list of channels or an error message.
        """
        client = self.user_client if use_user_token and self.user_client else self.bot_client

        try:
            # Call the conversations.list method
            result = client.conversations_list(
                types="public_channel,private_channel,mpim,im"
            )
            
            channels = []
            for channel in result["channels"]:
                if channel.get("name"):
                        channels.append({
                        "id": channel["id"],
                        "name": channel["name"]
                    })

            return {"channels": channels}

        except SlackApiError as e:
            return {"error": f"Error listing channels: {e}"}

    def get_channel_messages(self, channel: str, use_user_token: bool = False) -> Dict[str, Any]:
        """
        Retrieve all messages from a given channel.

        Args:
        channel (str): The name or ID of the Slack channel to get messages from.
        use_user_token (bool): If True, use the user token instead of the bot token. Defaults to False.

        Returns:
        Dict[str, Any]: A dictionary containing the messages (with sender information) or an error message.
        """
        client = self.user_client if use_user_token and self.user_client else self.bot_client

        try:
            # Get the channel ID if a channel name was provided
            if not channel.startswith('C') and not channel.startswith('D'):
                channel_id = client.conversations_list(types="public_channel,private_channel")
                channel_id = next((c['id'] for c in channel_id['channels'] if c['name'] == channel), None)
                if not channel_id:
                    return {"error": f"Channel '{channel}' not found"}
            else:
                channel_id = channel

            # Fetch messages
            result = client.conversations_history(channel=channel_id)
            
            messages = []
            for msg in result['messages']:
                sender_info = client.users_info(user=msg['user'])
                sender_name = sender_info['user']['real_name']
                messages.append({
                    'message': msg.get('text', ''),
                    'sender': sender_name,
                })

            return {"messages": messages}

        except SlackApiError as e:
            return {"error": f"Error getting channel messages: {e}"}

if __name__ == "__main__":
    slack = SlackAPI()
    channel = "social"
    message = "Hello from Python!"
    
    # Send message to channel
    result = slack.send_message(channel, message)
    print(result)
    # print(f"Send message result: {result}")

    # Send private message
    # user_id = "D085FE564CB"  # Replace with an actual user ID
    # private_message = "Hello, this is a private message!"
    # result = slack.send_private_message(user_id, private_message)
    # print(f"Send private message result: {result}")

    # # Get unread messages
    # result = slack.get_unread_messages(channel)
    # print(f"Get unread messages result: {result}")

    # List all channels
    result = slack.list_channels()
    print(f"List channels result: {result}")

    # Get all messages from a channel
    result = slack.get_channel_messages(channel)
    print(f"Get channel messages result: {result}")
