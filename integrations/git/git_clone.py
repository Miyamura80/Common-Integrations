from git import Repo
from git.exc import GitCommandError
import os
import shutil
from utils.replay.replay import Replay


def branch_exists(repo_path, branch_name):
    try:
        repo = Repo(repo_path)
        return branch_name in repo.refs
    except GitCommandError:
        print(
            f"Error: Unable to check branch '{branch_name}' in repository at '{repo_path}'"
        )
        return False


def git_temp_clone(repo: str) -> str:
    """
    Clones the given GitHub repository into a temporary directory and returns the path to that directory.

    Args:
        repo (str): The URL of the GitHub repository to clone.

    Returns:
        str: The path to the temporary directory where the repository was cloned.
    """
    repo_name = repo.split("/")[-1]
    repo_path = f"/tmp/{repo_name}"

    # Check if the directory already exists
    if os.path.exists(repo_path):
        # If it exists, check if the main branch exists to avoid re-cloning
        if branch_exists(repo_path, "main"):
            print(f"Using existing repository at {repo_path}")
            repo = Repo(repo_path)
            main_branch = repo.heads["main"]
            main_branch.checkout()
            repo.head.reset("origin/main", index=True, working_tree=True)
            print(f"Reset to main branch and pulled latest changes!")
        elif branch_exists(repo_path, "master"):
            print(f"Using existing repository at {repo_path}")
            repo = Repo(repo_path)
            master_branch = repo.heads["master"]
            master_branch.checkout()
            repo.head.reset("origin/master", index=True, working_tree=True)
            print(f"Reset to master branch and pulled latest changes!")
        else:
            print(f"Repository at {repo_path} does not have main or master branch")
            print(f"Cloning repository from {repo}")
            shutil.rmtree(repo_path)
            repo = Repo.clone_from(repo, repo_path)
            print(f"Cloned repository from {repo} to {repo_path}!")
    else:
        print(f"Cloning repository from {repo} to {repo_path}")
        repo = Repo.clone_from(repo, repo_path)
        print(f"Cloned repository from {repo} to {repo_path}!")

    if Replay.instance_exists() and Replay.get_instance().is_recording():
        Replay.get_instance().compress_source(repo_path)

    return repo_path
