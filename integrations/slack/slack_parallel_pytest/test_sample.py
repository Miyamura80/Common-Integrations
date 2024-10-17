# test_sample.py
import time
from integrations.slack.slack import Slack

slack = Slack()


def test_example1(thread_ts, parallel_add_totals):
    time.sleep(1)
    slack.send_thread_reply("eval-results", thread_ts, f"Reply {thread_ts} 1\n")
    parallel_add_totals(1, 2)
    assert True


def test_example2(thread_ts, parallel_add_totals):
    time.sleep(5)
    slack.send_thread_reply("eval-results", thread_ts, "Reply 2\n")
    parallel_add_totals(10, 20)
    assert True


def test_example3(thread_ts, parallel_add_totals):
    time.sleep(1)
    slack.send_thread_reply("eval-results", thread_ts, "Reply 3\n")
    parallel_add_totals(100, 200)
    assert True
