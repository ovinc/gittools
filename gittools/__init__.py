"""Tools for using GIT in python, based on gitpython.

Functions
---------
The module is designed to use mainly the function current_commit_hash()
but path_in_tree() is also made available in case it proves useful. See
help of these functions and README file for documentation and examples.
"""

from .gittools import path_in_tree, DirtyRepo, NotInTree
from .gittools import current_commit_hash, module_git_status

__version__ = 0.2
