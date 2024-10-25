"""
Slack Integration Module

This module provides a Slack class for interacting with the Slack API.
It allows sending messages, uploading files, and retrieving channel IDs.

Dependencies:
- global_config: For accessing the Slack bot token
- slack_sdk: For interacting with the Slack API

Usage:
    slack = Slack()
    slack.send_message("#channel-name", "Hello, Slack!")
    slack.send_file("#channel-name", "path/to/file.txt", "Check out this file")
    channel_id = slack._get_channel_id("#channel-name")

Note: Ensure that the SLACK_BOT_TOKEN is properly set in the global configuration.
"""

from global_config import global_config
from slack_sdk import WebClient
from typing import Optional

import warnings


class Slack:
    """
    A class to interact with the Slack API.

    Attributes:
        client (WebClient): An instance of the Slack WebClient.
    """

    def __init__(self):
        """
        Initializes the Slack client with the bot token from global configuration.
        """
        self.client = WebClient(token=global_config.SLACK_BOT_TOKEN)

    def send_message(self, channel_name: str, text: str) -> Optional[str]:
        """
        Sends a message to a specified Slack channel and returns the message ID.

        Args:
            channel (str): The name or ID of the channel to send the message to.
            text (str): The message text to send.

        Returns:
            str: The message ID (timestamp) of the sent message.

        Raises:
            SlackApiError: If there's an error sending the message.
        """
        if not self._check_channel_exists(channel_name):
            raise ValueError(f"Channel '{channel_name}' does not exist")

        if channel_name.startswith("#"):
            channel_name = channel_name[1:]

        response = self.client.chat_postMessage(channel=channel_name, text=text)
        return response["ts"]

    def send_file(self, channel_name, file_path, initial_comment) -> Optional[str]:
        """
        Uploads a file to a specified Slack channel and returns the thread timestamp.

        Args:
            channel (str): The name or ID of the channel to upload the file to.
            file_path (str): The path to the file to be uploaded.
            initial_comment (str): A comment to accompany the file upload.

        Returns:
            str: The thread timestamp that can be used for replies.

        Raises:
            SlackApiError: If there's an error uploading the file.
        """
        if channel_name.startswith("#"):
            channel_name = channel_name[1:]

        if not self._check_channel_exists(channel_name):
            raise ValueError(f"Channel '{channel_name}' does not exist")

        channel_id = self._get_channel_id(channel_name)

        # Upload the file
        file_upload = self.client.files_upload_v2(
            channel=channel_id,  # Use channel ID here
            file=file_path,
            initial_comment=initial_comment,
        )

        return file_upload["file"]["timestamp"]

    def send_thread_reply(self, channel_name: str, thread_ts: str, text: str) -> str:
        """
        Sends a reply to a thread in a specified Slack channel.
        WARNING: If thread_ts is None, it will not raise an error, instead it sends on channel

        Args:
            channel_name (str): The name or ID of the channel containing the thread.
            thread_ts (str): The timestamp of the parent message to reply to.
            text (str): The message text to send as a reply.

        Returns:
            str: The message ID (timestamp) of the sent reply message.

        Raises:
            SlackApiError: If there's an error sending the message.
        """
        if channel_name.startswith("#"):
            channel_name = channel_name[1:]

        if not self._check_channel_exists(channel_name):
            raise ValueError(f"Channel '{channel_name}' does not exist")
        if not thread_ts:
            raise ValueError("thread_ts is required")

        response = self.client.chat_postMessage(
            channel=channel_name, text=text, thread_ts=thread_ts
        )

        if response["ts"] is None:
            warnings.warning("Failed to send thread reply: response timestamp is None")

        return response["ts"]

    def edit_message(self, channel_name: str, message_ts: str, new_text: str) -> bool:
        """
        Edits an existing message in a specified Slack channel.

        Args:
            channel_name (str): The name or ID of the channel containing the message.
            message_ts (str): The timestamp of the message to be edited.
            new_text (str): The new text to replace the original message content.

        Returns:
            bool: True if the message was successfully edited, False otherwise.

        Raises:
            SlackApiError: If there's an error editing the message.
        """
        if channel_name.startswith("#"):
            channel_name = channel_name[1:]

        if not self._check_channel_exists(channel_name):
            raise ValueError(f"Channel '{channel_name}' does not exist")

        if not message_ts:
            raise ValueError("message_ts is required")

        channel_id = self._get_channel_id(channel_name)
        if not channel_id:
            print(f"Error: Channel '{channel_name}' not found.")
            return False

        response = self.client.chat_update(
            channel=channel_id, ts=message_ts, text=new_text
        )
        return response["ok"]

    def _get_channel_id(self, channel_name: str) -> Optional[str]:
        """
        Checks if a channel exists by name.
        """
        if channel_name.startswith("#"):
            channel_name = channel_name[1:]

        channels = self.client.conversations_list()
        channel_id = None
        for channel in channels["channels"]:
            if channel["name"] == channel_name:
                channel_id = channel["id"]
                break

        return channel_id

    def _check_channel_exists(self, channel_name: str) -> bool:
        """
        Checks if a channel exists by name.
        """
        return self._get_channel_id(channel_name) is not None


if __name__ == "__main__":
    slack = Slack()
    print(slack._get_channel_id("#eval-results"))
