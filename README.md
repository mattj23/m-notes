# M-Notes

M-Notes is a command line tool for performing operations on large corpuses of markdown notes, such as the type managed by tools like [Zettlr](https://github.com/Zettlr/Zettlr).  M-Notes takes advantage of YAML formatted front-matter to store metadata in the file itself rather than require a separate database. This was a delibrate choice to retain compatibility with flat text version control tools like git.

M-Notes is an opinionated piece of software originally written to manage the exodus of a very large (several thousand notes) body of notes from Evernote while reconstructing the internal linking with a different unique set of primary keys.  Currently M-Notes handles the creation and enforcement of a creation-time based unique key index for notes and can generate and re-name files with these keys.

Future features will include the generation of backlinks, file name generation, watching for changes, archiving/backups to compressed files or git repositories. 

## Installation
M-Notes requires at least Python 3.7

To install M-Notes, it's easiest to create a virtual environment, though it can be installed directly to the system via `pip`

### Linux & MacOS

```bash
# Skip this if you're not going to use a virtual environment
$ python3 -m venv mnote
$ source mnote/bin/activate

# Install via pip from this github repository
(mnote) $ pip install git+https://github.com/mattj23/m-notes
```


## Usage

If you used a virtual environment during installation it needs to be active to use the tool. The command-line tool is `mnote` and lives in the python script binary.

```bash
# Navigate into a working directory containing your notes
(mnote) $ mnote --help

```

M-Note's default when run without arguments is to summarize the corpus of notes. If problems are found they will be displayed with a hint message showing the commands to fix them.



