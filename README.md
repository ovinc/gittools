Tools for using GIT in python, based on *gitpython*.

Functions
---------

`file_in_commit(file, commit)`

Return True if file belongs to the commit's working tree, else False.

**Inputs**
- file: str or path object
- commit: *gitpython* commit object

---

`parent_repo(file)`

Return repository object if file is in a (sub)folder of a GIT repo.

**Input**
- file: str or path object

**Output**
- repo: *gitpython* object of the *Repo* class, or None for inexistent repo.

---

`current_commit_hash(file, dirtyok=False)`

Return HEAD commit hash corresponding to file if it's in a GIT repo.

**Input**
- file: str or path object
- dirtyok: bool, if True exception raised if repo has uncommitted changes.

**Output**
- str of the commit's hash name.


Install
-------

- Clone the project or download directly the files into a folder.
- In a terminal, `cd` into the project's folder (where the file
__setup.py__ is located).
- run `python -m pip install .` in the command line.

Now, the module can be imported in Python with `import gittools`.

**Note**: replace `python` with the command or alias corresponding to the Python installation you would like to install the package with.

**Note**: if you wish to keep the package files in the folder where the files
were downloaded and/or edit the files with direct effect in Python, run the
following install command instead: `python -m pip install -e .`.


Requirements
------------

- Python >= 3.6 (f-strings)
- gitpython (https://gitpython.readthedocs.io)
- see gitpython requirements for GIT minimal version.