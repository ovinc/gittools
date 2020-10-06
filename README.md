# General info

Tools for using git in python, based on *gitpython*.

Install
-------

### Method 1

In a terminal:
```bash
pip install git+https://cameleon.univ-lyon1.fr/ovincent/gittools
```

### Method 2

Clone the project or download directly the files into a folder.
In a terminal, cd into the project or folder, where the setup.py is, then

```bash
pip install .
```

- Clone the project or download directly the files into a folder.
- In a terminal, `cd` into the project's folder (where the file
__setup.py__ is located).
- run `python -m pip install .` in the command line.

Now, the module can be imported in Python with `import gittools`.

**Note**: replace `python` with the command or alias corresponding to the Python installation you would like to install the package with.

**Note**: if you wish to keep the package files in the folder where the files
were downloaded and/or edit the files with direct effect in Python, run the
following install command instead: `python -m pip install -e .`.


# Available functions

See help / docstrings of functions for details, and **Examples** section below.

```python
current_commit_hash(path='.', checkdirty=True, checktree=True)
```
commit hash (str) of HEAD commit of repository where path belongs; if True, `checkdirty` and `checktree` raise exceptions if repo is dirty and if path does not belong to repo's tree, respectively.

```python
path_status(path='.')
```
Similar to `current_commit_hash()` but does not raise exceptions. Instead, returns git status (commit hash, dirty or clean, tag if there is one) as a dictionary.

```python
module_status(module, warning=False)
```
Version of `path_status()` adapted for python modules (module can be a single module or a list/iterable of modules). Data is returned as a dict of dicts where the keys are module names and the nested dicts correspond to dicts returned by `path_status()`

```python
repo_tags(path='.')
```
Lists all tags in repository the path belongs to, as a {'commit hash': 'tag name'} dictionary (both keys and values are strings).

```python
path_in_tree(path, commit)
```
This function is used by *current_commit_hash* but is also made available in case it proves useful in some situations. Returns True if path belongs to the commit's working tree (or is the root directory of repo), else False.


Exceptions
----------

The `checkdirty` and `checktree` options raise custom exceptions: `DirtyRepo` and `NotInTree`, respectively.


# Examples

```python
>>> from gittools import current_commit_hash, repo_tags

>>> current_commit_hash()  # Most recent commit of the current working directory
'1f37588eb5aadf802274fae74bc4abb77ddd8004'

# Other possibilities
>>> current_commit_hash(checkdirty=False) # same, but avoid raising DirtyRepo
>>> current_commit_hash('gitrepos/repo1/foo.py') # same, but specify path/file

# Note that the previous example will raise an exception if the file is not
# tracked in a git repository. To silence the exception and see the most
# recent commit hash of the closest git repository in a parent directory:
>>> current_commit_hash('Test/untracked_file.pyc', checktree=False)

# List all tags of repo:
>>> repo_tags()  # current directory, but also possible to specify path
{'1f37588eb5aadf802274fae74bc4abb77ddd8004': 'v1.1.8',
 'b5173941c9cce9bb786b0c046c67ea505786d820': 'v1.1.9'}
```

It can be easier to use higher level functions to get hash name, clean/dirty status, and tag (if it exists):
```python
>>> from gittools import path_status, module_status

>>> path_status()  # current working directory (also possible to specify path)
{'hash': '1f37588eb5aadf802274fae74bc4abb77ddd8004',
 'status': 'clean',
 'tag': 'v1.1.8'}

>>> import mypackage1  # module with clean repo and tag at current commit
>>> module_status(mypackage1)
{'mypackage1': {'hash': '1f37588eb5aadf802274fae74bc4abb77ddd8004',
                'status': 'clean',
                'tag': 'v1.1.8'}}

>>> import mypackage2  # this package has uncommitted changes and no tags
>>> module_status(mypackage2, warning=True)
Warning: the following modules have dirty git repositories: mypackage2
{'mypackage2': {'hash': '8a0305e6c4e7a57ad7befee703c4905aa15eab23',
                'status': 'dirty'}}

>>> module_status([mypackage1, mypackage2]) # list of modules
{'mypackage1': {'hash': '1f37588eb5aadf802274fae74bc4abb77ddd8004',
                'status': 'clean',
                'tag': 'v1.1.8'},
 'mypackage2': {'hash': '8a0305e6c4e7a57ad7befee703c4905aa15eab23',
                'status': 'dirty'}}
```


# Requirements

- Python >= 3.6 (f-strings)
- gitpython (https://gitpython.readthedocs.io)
- see gitpython requirements for git minimal version.


# Author

Olivier Vincent (olivier.vincent@univ-lyon1.fr)