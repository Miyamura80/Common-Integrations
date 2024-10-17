import pytest
import os
import time
from filelock import FileLock
from integrations.slack.slack import Slack


thread_head = "Test Header"
slack = Slack()


def pytest_configure(config):
    config.cache.set("parallel_add_total_1", 0)
    config.cache.set("parallel_add_total_2", 0)
    # Clear the thread_ts at the start of each test run
    config.cache.set("thread_ts", None)


@pytest.fixture(scope="session")
def thread_ts(request):
    lock_file = "slack_thread.lock"
    with FileLock(lock_file):
        thread_ts = request.config.cache.get("thread_ts", None)
        if thread_ts is None:
            # Create a new thread only if it doesn't exist
            thread_ts = slack.send_message(
                "eval-results", thread_head + "🟡 Status: Running\n"
            )
            request.config.cache.set("thread_ts", thread_ts)
        return thread_ts


@pytest.fixture(scope="function")
def parallel_add_totals(request):
    def increment(amount1, amount2):
        with FileLock("parallel_add_totals.lock"):
            current_total1 = request.config.cache.get("parallel_add_total_1", 0)
            current_total2 = request.config.cache.get("parallel_add_total_2", 0)
            new_total1 = current_total1 + amount1
            new_total2 = current_total2 + amount2
            request.config.cache.set("parallel_add_total_1", new_total1)
            request.config.cache.set("parallel_add_total_2", new_total2)

    return increment


def pytest_sessionfinish(session, exitstatus):
    if not hasattr(session.config, "workerinput"):  # Only run on the main process
        thread_ts = session.config.cache.get("thread_ts", None)
        total1 = session.config.cache.get("parallel_add_total_1", 0)
        total2 = session.config.cache.get("parallel_add_total_2", 0)

        if thread_ts:
            slack.edit_message(
                "eval-results",
                thread_ts,
                thread_head
                + f"🟢 Status: Finished Running\nTotal 1: {total1}\nTotal 2: {total2}\n",
            )

    # Clean up lock files
    for lock_file in ["slack_thread.lock", "parallel_add_totals.lock"]:
        if os.path.exists(lock_file):
            os.remove(lock_file)
