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
(mnote) $ pip3 install git+https://github.com/mattj23/m-notes
```

To update to the latest version:

```
pip3 install git+https://github.com/mattj23/m-notes --upgrade
```



## Usage

If you used a virtual environment during installation it needs to be active to use the tool. The command-line tool is `mnote` and lives in the python script binary.

### Built-in Help
You can use the built in help features to get more information on M-Notes' various commands and options. Starting with the root command, `mnote`, the `--help` option will display the list of subcommands which can be run.
```bash
$ mnote --help
```

The `--help` option can be run on any subcommand, no matter how deep in the command structure.  For example:

```bash
$ mnote fix --help
$ mnote fix author --help
```

### Configuration

The config command allows you to set global information. To see what the options are, use the help option:

```bash
$ mnote config --help
```

Running `mnote config` by itself will display what the currently loaded configuration parameters are.

The default author can be set with:

```bash
$ mnote config --author "Jane C. Doe"
```

### Fixing Issues with Notes

There are various issues which notes in a corpus can have that cause problems for managing the overall collection and enforcing things like uniqueness and consistency.  The `mnote fix` command is a tool which can help quickly detect and resolve these issues.

**The `mnote fix` command operates only on your current working directory**. 

To scan the current working directory (recursively) for all problematic notes, run the base fix command:

```bash
$ mnote fix
```

The number of results displayed can be adjusted with the `-n` option:

```bash
$ mnote fix -n 50
```

Problems will be summarized and the commands to perform the fixes will be suggested. The available subcommands are currently:

|Command|Description|
|-|-|
|`mnote fix created`|Fix missing creation timestamps|
|`mnote fix id`|Fix missing IDs from the note metadata|
|`mnote fix title`|Attempt to fix missing titles by looking for an H1 line at the start of the note|
|`mnote fix author`|Add author to note either from the default author or one given with the `--author` option|
|`mnote fix filename`|Fix filenames missing their IDs. Also can clean up filenames with the `--complete` and `--force` options|

All `mnote fix` subcommands can be run on specific files, GLOB patterns (if your operating system supports it), or the entire directory contents:

```bash
# Run the command on every file in the current working directory
mnote fix <command> 

# Run the command on the first 10 files that have the specified issue in the working directory
mnote fix <command> -n 10

# Run the command on the file "my-note.md"
mnote fix <command> my-note.md

# Run the command on all files that match the pattern note*.md
mnote fix <command> note*.md

# Run the command on the first 3 files that match the pattern note*.md
mnote fix <command> note*.md -n 3

# Run the command on all files in the "test" subdirectory
mnote fix <command> ./test/*
```