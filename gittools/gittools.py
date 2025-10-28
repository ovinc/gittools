"""Git tools for Python."""

import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from warnings import warn

import importlib_metadata
from importlib_metadata import PackageNotFoundError
from git import Repo, InvalidGitRepositoryError

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


def is_iterable(x):
    """Check if x is iterable or not, returns bool"""
    try:
        iter(x)
    except TypeError:
        return False
    else:
        return True


def _make_iterable(x):
    """Transforms non-iterables into a tuple, but keeps iterables unchanged."""
    if is_iterable(x):
        return x
    else:
        return x,


def _get_version(module):
    """Get version of module, or of package containing module"""
    try:
        version = module.__version__
    except AttributeError:
        name = module.__name__
        if '.' in name:  # e.g. matplotlib.pyplot --> get matplotlib only
            name = name.split('.')[0]
        version = importlib_metadata.version(name)
    return version


# ============================= Public functions =============================


def path_in_tree(path, commit):
    """Return True if path belongs to the commit's working tree, else False.

    Note that if the path is the root directory of the git repository (where
    the .git is located), the function also returns True even if one could
    argue that the root directory is technically not in the repo's tree.

    Parameters
    ----------
    path : str or pathlib.Path
        path object of folder or file
    commit : gitpython commit object

    Returns
    -------
    bool
        True if path is in working tree, False if not
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

    Parameters
    ----------
    path : str or pathlib.Path
        folder/file. Default: current working dir.
    checkdirty : bool
        if True exception raised if repo has uncommitted changes.
    checktree : bool
        if True exception raised if path/file not in repo's working tree and
        path is not the root directory of the repo.

    Returns
    -------
    str
        commit's hash name.
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

    Parameters
    ----------
    path : str or pathlib.Path
        object of folder/file. Default: current working dir.

    Returns
    -------
    dict
        {'commit hash': 'tag name'} (both key and value are str).
    """
    p = _pathify(path)
    repo = Repo(p, search_parent_directories=True)

    return {str(tag.commit): str(tag) for tag in repo.tags}


def path_status(path='.'):
    """Current (HEAD) commit hashes, status (dirty or clean), and potential tag.

    Slightly higher level compared to current_commit_hash, as it returns a
    dictionary with a variety of information (status, hash, tag)

    Parameters
    ----------
    path : str or pathlib.Path
        object of folder/file. Default: current working dir.

    Returns
    -------
    dict
        dictionary with keys 'hash', 'status' (clean/diry), 'tag' (if exists)
    """
    info = {}

    # get commit hash and check repo status (dirty or clean) -----------------
    try:
        cch = current_commit_hash(path, checkdirty=True)
    except DirtyRepo:
        cch = current_commit_hash(path, checkdirty=False)
        status = 'dirty'
    else:
        status = 'clean'

    info['hash'] = cch
    info['status'] = status

    # check if tag associated with commit ------------------------------------
    commits_with_tags = repo_tags(path)
    if cch in commits_with_tags:
        info['tag'] = commits_with_tags[cch]

    return info


def module_status(module, nogit_ok=True):
    """Get status info (current hash, dirty/clean repo, tag) of python module

    (can be a module or a full package)

    Parameters
    ----------
    module : module or package
        python module/package

    nogit_ok : bool
        if True (default), replace gitr info with version number of module
        if False, raise InvalidGitRepositoryError if module not git-versioned

    Returns
    -------
    dict
        dict with keys 'hash', 'status', 'tag'
        If not in a git repo, the status will say 'not a git repository'
        and the key 'hash' will not exist, and 'tag' will contain the
        package version number if it exists (if not, 'tag' key will not exist)
    """
    try:
        info = path_status(module.__file__)
    except InvalidGitRepositoryError:
        if not nogit_ok:
            raise InvalidGitRepositoryError(f'{module} not a git repo')
        info = {'status': 'not a git repository'}
    else:
        return info

    try:
        version = _get_version(module)
    except PackageNotFoundError:
        tag_info = {}
    else:
        tag_info = {'tag': f'v{version}'}

    return {**info, **tag_info}


# ================== Functions for status of python modules ==================


def check_modules(
    modules,
    dirty_ok=False,
    dirty_warning=False,
    notag_warning=False,
    nogit_ok=False,
    nogit_warning=False,
):
    """Get status info (current hash, dirty/clean repo, tag) of module(s).

    Parameters
    ----------
    module : iterable of modules/packages
        modules and/or packages to check for version information

    dirty_warning : bool
        if True, prints a warning if some git repos are dirty.

    dirty_ok : bool
        if False, raise an error if module(s) is/are dirty.

    notag_warning : bool
        if True, prints a warning if some git repos don't have tags

    nogit_ok : bool
        if True, if some modules are not in a git repo, simply get
        their version number. If False (default), raise an error.

    nogit_warning : bool
        if some modules are not in a git repo and nogit_ok is True,
        print a warning when this happens.

    Returns
    -------
    dict
        module name as keys, and a dict {hash:, status:, tag:} as values
    """
    info_modules = {
        module.__name__: module_status(module, nogit_ok=nogit_ok)
        for module in modules
    }

    # Manage warnings if necessary -------------------------------------------

    if dirty_warning or not dirty_ok:

        dirty_modules = [
            module for module, info in info_modules.items()
            if info['status'] == 'dirty'
        ]

        if len(dirty_modules) > 0:

            msg = (
                'These modules have dirty git repositories: '
                f"{', '.join(dirty_modules)}"
            )

            if not dirty_ok:
                raise DirtyRepo(msg)
            else:
                warn(msg, stacklevel=2)

    if notag_warning:

        tagless_modules = [
            module for module, info in info_modules.items()
            if 'tag' not in info
        ]

        if len(tagless_modules) > 0:
            warn(
                'Warning: these modules are missing a tag: '
                f"{', '.join(tagless_modules)}",
                stacklevel=2,
            )

    if nogit_ok and nogit_warning:

        nogit_modules = [
            module for module, info in info_modules.items()
            if info['status'] == 'not a git repository'
        ]

        if len(nogit_modules) > 0:
            warn(
                'Warning: these modules are not in a git repository: '
                f"{', '.join(nogit_modules)}",
                stacklevel=2,
            )

    return info_modules


def save_metadata(
    file,
    info=None,
    module=None,
    modules=None,
    dirty_warning=False,
    dirty_ok=False,
    notag_warning=False,
    nogit_ok=False,
    nogit_warning=False,
):
    """Save metadata (info dict) into json file, and add git commit & time info.

    Parameters
    ----------
    file : str or pathlib.Path
        .json file to save data into.

    info : dict
        misc. info to save into the json file along module information

    module : python package
        module or iterable (e.g. list) of modules with git info to save.

    dirty_warning : bool
        if True, prints a warning if some git repos are dirty.

    dirty_ok : bool
        if False, raise an error if module(s) is/are dirty.

    notag_warning : bool
        if True, prints a warning if some git repos don't have tags

    nogit_ok : bool
        if True, if some modules are not in a git repo, simply get
        their version number. If False (default), raise an error.

    nogit_warning : bool
        if some modules are not in a git repo and nogit_ok is True,
        print a warning when this happens.

    Returns
    -------
    None
    """
    if module is not None:
        warn(
            "Future version of gittools.save_metadata() will not accept "
            "the module= argument, only modules= with an iterable of modules",
            category=DeprecationWarning,
            stacklevel=2,
        )
        modules = _make_iterable(module)

    metadata = info.copy() if info is not None else {}
    metadata['time (utc)'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    # Info on commit hashes of homemade modules used -------------------------
    if modules is not None:
        metadata['code version'] = check_modules(
            modules,
            dirty_warning=dirty_warning,
            dirty_ok=dirty_ok,
            notag_warning=notag_warning,
            nogit_ok=nogit_ok,
            nogit_warning=nogit_warning,
        )

    # Write to file ----------------------------------------------------------
    # Note: below, the encoding and ensure_ascii options are for signs like °
    with open(file, 'w', encoding='utf8') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
