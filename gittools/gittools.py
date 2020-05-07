"""Git tools for Python."""

from warnings import warn

from pathlib import Path

from git import Repo
from git import InvalidGitRepositoryError


def file_in_commit(file, commit):
    """Return True if file belongs to the commit's working tree, else False.

    **Inputs**
    - file: str or path object
    - commit: *gitpython* commit object
    """

    fileabs = Path(file).resolve()  # absolute path of filename
    rootabs = Path(commit.repo.working_dir).resolve()  # path of root of repo
    localname = str(fileabs.relative_to(rootabs))  # name of file in the repo

    if not fileabs.exists():
        raise FileNotFoundError(f'File {fileabs} does not exist')

    try:
        commit.tree[localname]
    except KeyError:  # in this case the file is not in the commit
        return False
    else:
        return True


def parent_repo(file):
    """Return repository object if file is in a (sub)folder of a GIT repo.

    **Input**
    - file: str or path object

    **Output**
    - repo: *gitpython* object of the *Repo* class, or None for inexistent repo.
    """

    filepath = Path(file)

    try:
        repo = Repo(filepath, search_parent_directories=True)
    except InvalidGitRepositoryError:
        warn('No git repository found. Returning None.')
        return None
    else:
        return repo


def current_commit_hash(file, dirtyok=False):
    """Return HEAD commit hash corresponding to file if it's in a GIT repo.

    **Input**
    - file: str or path object
    - dirtyok: bool, if True exception raised if repo has uncommitted changes.

    **Output**
    - str of the commit's hash name.
    """

    repo = parent_repo(file)
    if not dirtyok and repo.is_dirty():
        raise Exception("Dirty repo, please commit recent changes first.")

    commit = repo.head.commit
    assert file_in_commit(file, commit), "File not in working tree."

    return str(commit)


