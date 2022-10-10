from git import Repo
import logging
import os
import shutil
import time
from string import Template
import copy
import requests

# TODO: Clean up legacy MAAP code
"""
def git_clone(repo_url=settings.GIT_REPO_URL, repo_name=settings.REPO_NAME):
    GITLAB_TOKEN = settings.GITLAB_TOKEN
    git_url = Template(repo_url).substitute(TOKEN=GITLAB_TOKEN)
    repo_path = os.path.join(settings.REPO_PATH, repo_name)
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)
    repo = Repo.clone_from(git_url, repo_path, c='http.sslverify=false')
    return repo
"""


def update_git_repo(repo, repo_path, repo_name, algorithm_name):
    file_list = [
        '{}/{}/docker/hysds-io.json.{}'.format(repo_path, repo_name, algorithm_name),
        '{}/{}/docker/job-spec.json.{}'.format(repo_path, repo_name, algorithm_name)
    ]

    try:
        commit_message = 'Registering algorithm: {}'.format(algorithm_name)
        repo.index.add(file_list)
        repo.index.commit(commit_message)
        origin = repo.remote('origin')
        origin.push()
    except Exception as ex:
        raise Exception("Failed to push changes to git.")
    headcommit = repo.head.commit
    commithash = headcommit.hexsha
    return commithash


"""
def clean_up_git_repo(repo, repo_name):
    files_list = os.listdir(os.path.join(settings.REPO_PATH, repo_name, "docker"))
    print(files_list)
    for file in files_list:
        if file != "Dockerfile":
            print("Removing file : {}".format(file))
            os.remove('{}/{}/docker/{}'.format(settings.REPO_PATH, repo_name, file))
            repo.index.remove(['{}/{}/docker/{}'.format(settings.REPO_PATH, repo_name, file)])
    return repo"""
