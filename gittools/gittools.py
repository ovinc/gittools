"""Git tools for Python."""

from warnings import warn
from pathlib import Path, PurePosixPath
from git import Repo


class DirtyRepo(Exception):
    """Specific exception indicating some changes in repo are not committed."""
    pass


class NotInTree(Exception):
    """Specific exception indicating file is not in commit tree."""
    pass


def _pathify(path):
    """Transforms str or partial path in fully resolved path object."""
    pathabs = Path(path).resolve()  # absolute path of filename
    if not pathabs.exists():
        raise FileNotFoundError(f'Path {pathabs} does not exist')
    return pathabs


def _make_iterable(x):
    """Transforms non-iterables into a tuple, but keeps iterables unchanged."""
    try:
        iter(x)
    except TypeError:
        return x,
    else:
        return x


def path_in_tree(path, commit):
    """Return True if path belongs to the commit's working tree, else False.

    Note that if the path is the root directory of the git repository (where
    the .git is located), the function also returns True even if one could
    argue that the root directory is technically not in the repo's tree.

    **Inputs**
    - path: str or path object of folder or file
    - commit: *gitpython* commit object
    """

    pathabs = _pathify(path)
    rootabs = Path(commit.repo.working_dir).resolve()  # path of root of repo

    localpath = pathabs.relative_to(rootabs)  # relative path of file in repo
    localname = str(PurePosixPath(localpath))  # gitpython uses Unix names

    if localname == '.':  # Means that the entered path is the repo's root
        return True

    try:
        commit.tree[localname]
    except KeyError:  # in this case the file is not in the commit
        return False
    else:
        return True


def current_commit_hash(path=None, checkdirty=True, checktree=True):
    """Return HEAD commit hash corresponding to path if it's in a GIT repo.

    **Input**
    - path: str or path object of folder or file. If None (default), it is
    considered to be the current working directory.
    - checkdirty: bool, if True exception raised if repo has uncommitted changes.
    - checktree: bool, if True exception raised if path/file not in repo's
    working tree and path is not the root directory of the repo.

    **Output**
    - str of the commit's hash name.
    """

    if path is None:
        path = '.'

    p = _pathify(path)
    repo = Repo(p, search_parent_directories=True)

    if checkdirty and repo.is_dirty():
        raise DirtyRepo("Dirty repo, please commit recent changes first.")

    commit = repo.head.commit

    if checktree and not path_in_tree(path, commit):
        raise NotInTree("Path or file not in working tree.")

    return str(commit)


def module_git_status(module, warning=False):
    """Get current commit hashes and status (dirty or clean) of list of modules.

    INPUT
    -----
    module or list/iterable of modules (each must belong to a git repository)
    warning: if True, prints a warning if some git repos are dirty.

    OUTPUT
    ------
    Dictionary with module name as keys, and a dict {hash:, status:} as values
    """
    modules = _make_iterable(module)
    dirty_repos = []
    infos = {}

    for module in modules:

        name = module.__name__
        try:
            commit = current_commit_hash(module.__file__)
        except DirtyRepo:
            commit = current_commit_hash(module.__file__, checkdirty=False)
            status = 'dirty'
            dirty_repos.append(name)
        else:
            status = 'clean'

        info = {'hash': commit, 'status': status}
        infos[name] = info

    if warning and len(dirty_repos) > 0:
        msg = '\nWarning: the following modules have dirty GIT repositories: '
        msg += ', '.join(dirty_repos)
        print(msg)

    return infos
