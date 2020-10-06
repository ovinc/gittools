"""Git tools for Python."""


from warnings import warn
from pathlib import Path, PurePosixPath
from git import Repo


# ============================ Custom exceptions =============================


class DirtyRepo(Exception):
    """Specific exception indicating some changes in repo are not committed."""
    pass


class NotInTree(Exception):
    """Specific exception indicating file is not in commit tree."""
    pass


# =========================== Private subroutines ============================


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


# ============================= Public functions =============================


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


def current_commit_hash(path='.', checkdirty=True, checktree=True):
    """Return HEAD commit hash corresponding to path if it's in a git repo.

    INPUT
    -----
    - path: str or path object of folder/file. Default: current working dir.
    - checkdirty: bool, if True exception raised if repo has uncommitted changes.
    - checktree: bool, if True exception raised if path/file not in repo's
    working tree and path is not the root directory of the repo.

    OUTPUT
    ------
    - str of the commit's hash name.
    """
    p = _pathify(path)
    repo = Repo(p, search_parent_directories=True)

    if checkdirty and repo.is_dirty():
        raise DirtyRepo("Dirty repo, please commit recent changes first.")

    commit = repo.head.commit

    if checktree and not path_in_tree(path, commit):
        raise NotInTree("Path or file not in working tree.")

    return str(commit)


def repo_tags(path='.'):
    """Return dict of all {'commit hash': 'tag name'} in git repo.

    INPUT
    -----
    - path: str or path object of folder/file. Default: current working dir.

    OUTPUT
    ------
    dict  {'commit hash': 'tag name'} (both key and value are str).
    """
    p = _pathify(path)
    repo = Repo(p, search_parent_directories=True)

    return {str(tag.commit): str(tag) for tag in repo.tags}


def path_status(path='.'):
    """Current (HEAD) commit hashes, status (dirty or clean), and potential tag.

    Slightly higher level compared to current_commit_hash, as it returns a
    dictionary with a variety of information (status, hash, tag)

    INPUT
    -----
    - path: str or path object of folder/file. Default: current working dir.

    OUTPUT
    ------
    Dictionary keys 'hash', 'status' (clean/diry), 'tag' (if exists)
    """
    infos = {}

    # get commit hash and check repo status (dirty or clean) -----------------
    try:
        cch = current_commit_hash(path)
    except DirtyRepo:
        cch = current_commit_hash(path, checkdirty=False)
        status = 'dirty'
    else:
        status = 'clean'

    infos['hash'] = cch
    infos['status'] = status

    # check if tag associated with commit ------------------------------------
    commits_with_tags = repo_tags(path)
    if cch in commits_with_tags:
        infos['tag'] = commits_with_tags[cch]

    return infos


def module_status(module, warning=False):
    """Get status info (current hash, dirty/clean repo, tag) of module(s).

    INPUT
    -----
    - module or list/iterable of modules (each must belong to a git repository)
    - warning: if True, prints a warning if some git repos are dirty.

    OUTPUT
    ------
    Dict with module name as keys, and a dict {hash:, status:, tag:} as values
    """
    modules = _make_iterable(module)
    mods = {}

    for module in modules:
        name = module.__name__
        infos = path_status(module.__file__)
        mods[name] = infos

    dirty_repos = [m for m in mods if mods[name]['status'] == 'dirty']

    if warning and len(dirty_repos) > 0:
        msg = '\nWarning: the following modules have dirty git repositories: '
        msg += ', '.join(dirty_repos)
        print(msg)

    return mods
