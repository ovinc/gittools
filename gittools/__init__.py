"""Tools for using GIT in python, based on gitpython."""

from .gittools import DirtyRepo, NotInTree
from .gittools import current_commit_hash, path_status, module_status
from .gittools import repo_tags, path_in_tree
from .gittools import save_metadata

__version__ = '0.4.0'
