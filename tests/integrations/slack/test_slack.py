import unittest
from integrations.slack.slack import Slack
from tests.test_class import TestCaseClass, ci_test


class TestSlack(TestCaseClass):
    def setUp(self) -> None:
        super().setUp()
        self.slack = Slack()
        self.channel_name = "ignore-test-channel"

    @ci_test
    def test_send_message(self):
        """Test sending a message to a channel after joining it"""
        current_function = self.id().split(".")[
            -1
        ]  # Gets the current test function name
        message = (
            f"Unit Test at `{__file__}` in {current_function}: This is a test message"
        )

        # Test message send
        thread_ts = self.slack.send_message(self.channel_name, message)

        # Only check the assertion if we didn't get a SlackApiError
        self.assertIsNotNone(thread_ts, "Message should be sent successfully")

        # Reply to the message
        reply_message = "This is a reply to the message"
        reply_ts = self.slack.send_thread_reply(
            self.channel_name, thread_ts, reply_message
        )
        self.assertIsNotNone(reply_ts, "Reply should be sent successfully")

    @ci_test
    def test_send_file(self):
        """Test sending a file to a channel"""
        current_function = self.id().split(".")[
            -1
        ]  # Gets the current test function name
        message = (
            f"Unit Test at `{__file__}` in {current_function}: This is a test message"
        )

        # Test file upload
        thread_ts = self.slack.send_file(self.channel_name, "media/image.png", message)

        # WARNING: Replying to a file with Python SDK is not supported...
        # It's convoluted for no reason

        self.assertIsNotNone(thread_ts, "File should be sent successfully")


if __name__ == "__main__":
    unittest.main()
