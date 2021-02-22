# M-Notes

M-Notes is a command line tool for performing operations on large corpuses of markdown notes, such as the type managed by tools like [Zettlr](https://github.com/Zettlr/Zettlr).  M-Notes takes advantage of YAML formatted front-matter to store metadata in the file itself rather than require a separate database. This was a delibrate choice to retain compatibility with flat text version control tools like git.

M-Notes is an opinionated piece of software originally written to manage the exodus of a very large (several thousand notes) body of notes from Evernote while reconstructing the internal linking with a different unique set of primary keys.  Currently M-Notes handles the creation and enforcement of a creation-time based unique key index for notes and can generate and re-name files with these keys.

Current features:
* Manages and fixes front-matter keys like title/author/creation time, fixes file names in a standard way
* Enforces and creates unique IDs for notes for use in linking
* Performs note fixing with a transaction model: shows what's happening and allows the user to accept or reject all changes together
* Can be given many separate folders of notes to manage as a single global directory of files, performing operations across the global directory as if it was a single unified database
* Can zip and archive the entire global directory of notes with a single command
* Can generate backlinks across the entire global directory
* Many configuration and customization options

Planned features:
* Interactive link graphs for exploring the connective structure of the notes
* Compose large documents as "composite" documents, generated by including the content of other notes into a template through a special linking system, much like Scrivner's card system
* Rebuild broken file links, and optionally convert linked files to a uuid-based file naming system which can be easily rebuilt when broken

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

To remove:

```
pip3 uninstall m-notes
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

#### Default Author
The default author can be set with:

```bash
$ mnote config author "Jane C. Doe"
```

#### Filename "Complete" Default
The `mnote fix filename` and `mnote fix all` commands take a flag named `--complete`, which determines if M-Notes will completely recreate the file name from the note title when inserting the ID. This can be set to the default behavior (so that the `--complete` flag can be left out) with the following command:
``` bash
$ mnote config filename-complete on
```
Use `off` to turn it off again.

#### Text Styles
M-Notes allows you to customize certain text styles which are used through the program.  There are currently four text styles: `warning`, `visible`, `success`, and `fail`. 

The style setting is comprehensive.  See the Appendix at the end of this documnt for details.

### Indicies and the Global Directory
M-Notes will only work with markdown files that are in *indices*.  An *index* is a single folder on your computer which you tell M-Notes that you want to consider as part of your total corpus of notes. All of the markdown files in that directory and its subdirectories will be considered as part of the index.

The total combination of all indices on your computer together form the *global directory*. The *global directory* is the sum total of all markdown notes in all indicies on the computer.  It is the scope in which IDs must be unique and which backlinks can be computed.

M-Notes will not operate on notes that are not part of the *global directory*, so there must be at least one *index* before M-Notes will do anything.

> Indices form the basis of a caching structure. M-Notes stores file creation time and size information as well as the metadata from any YAML front-matter in a special file in the M-Notes configuration directory. When M-Notes starts it loads these cached files and then only reloads files who appear to have changed since the cache was made. This dramatically speeds up M-Notes' operations, but the `reload` command (see below) can be used to ensure that the cache is updated.

#### Creating an Index
An index can be created by navigating to the folder of interest and using the create command.
```bash
$ cd example-notes-folder/
$ mnote index create <index-name>
```

An index must have a name that includes lowercase letters, numbers, and dashes only. An index's name is an alias or shortcut for you. It should be quick to type and easy to remember.  

There are two other prerequisites for an index to be created, and they will be checked when the `mnote index create` command is run.
1. An index cannot contain another index. Thus you cannot create an index in a subfolder of an existing index, or in a parent folder of an existing index.
2. An new index will not be created if it has notes that IDs which conflict with notes that are *already* in the global directory. M-Notes will warn you about the conflicting notes, but it won't know how to resolve the conflicts.

If these conditions are satisfied M-Notes will create the index.

#### View Existing Indicies / Global Directory

A summary of the global directory can be displayed with the bare command:

```bash
$ mnote index
```

It will list all of the different indices, their names, folder paths, and the number of notes in each.

#### Delete an Index
An index can be removed from the global directory by using the remove command.

```bash
$ mnote index delete <index-name>
```

This will remove the index as a place in the global directory, meaning that M-Notes will no longer operate on markdown files in the folder which used to be mapped by the now-removed index.  The markdown files will be left untouched.

There is no real consequence to adding, removing, and then adding an index again by the same or different name. The only thing that will happen is that the cache may have to be rebuilt on the next run, which might take a few extra seconds.

#### Rebuild an Index

The caching of the indices works on looking at the file modification time and size reported by the operating system.  This is how tools like `rsync` work, however there is the possibility that the information inside the file has changed and the size/time method hasn't caught it. If you suspect this is the case, quickly running the reload command will ensure that everything is up to date.

```bash
$ mnote index reload
```

#### Zip Archiving an Index

A quick command to zip up all markdown notes in an index into a single archive file is provided.  It can be run with the names of a specific index/indices, or left blank to zip all of them.  The zip file will be named with the index name and a timestamp and saved in the current working directory.

You do not need to be in any of the index folders to run the command.  You can run in from any folder on your computer and it will save the arcived zip files to where you are.

```bash
# Zip all indices into separate files
$ mnote index zip

# Zip a single or multiple indices by name
$ mnote index zip <index-name> <index-name-2> ...
```

### Generating Backlinks

Backlinks are placed in a section at the end of markdown files that contains a horizontal rule and a H1 line starting with the words "M-Notes References". Everything below the horizontal rule is automatically generated and will be deleted when the links are updated.

Backlinks are generated for all files in the index which have a `backlinks: true` key in the YAML front-matter. Files without this key are left untouched.

The key can be batch added to files in the current directory and its subdirectories (assuming they are part of an index) with the following command:

```bash
$ mnote backlink set on
```

Alternatively the key can be removed by specifying `off` instead of `on`.

Backlinks are generated across the entire global directory at once.  This can be done with the following command:

```bash
$ mnote backlink gen
```
Files will only be written if the backlink content has changed.


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
|`mnote fix all`|Is the equivalent of running `created`, `id`, `title`, `author`, and `filename` in sequence, but will only run on up to 5 notes at a time to avoid problems|

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

---

## Appendix

### Configuring Text Styles
M-Notes allows you to customize certain text styles which are used through the program.  There are currently four text styles: `warning`, `visible`, `success`, and `fail`. 

The current configuration of the text styles can be displayed as follows.
```bash
# Display all styles as they are currently configured
$ mnote config style

# Display one or more of the text styles
$ mnote config style <style name> [<style name 2>, ...]

# For example, both of the following are valid:
$ mnote config style warning
$ mnote config style success fail
```

Colors show up differently on different terminals with different themes. To see what the ANSI colors look like on your display, run the following command:

```bash
$ mnote config style --colors
```

The actual properties for styles can be set by command line arguments while specifying one or more style names. Use `mnote config style --help` to see what each option does.

|Option|Value|Effect|
|-|-|-|
|`--fg`|color name (string)|Sets foreground (text) color. Run the `--colors` option to see availible colors|
|`--bg`|color name (string)|Sets background color. Run the `--colors` option to see availible colors|
|`--bold`|`true` or `false`|Turns on or off bold|
|`--underline`|`true` or `false`|Underlines the text|
|`--blink`|`true` or `false`|Makes the text blink|
|`--reverse`|`true` or `false`|Reverses the foreground and background colors, this can act like a highlighter|

##### Example of Setting Style Parameters

```bash
# Make the warning text red
$ mnote config style warning --fg red

# Make the visible text style blink
$ mnote config style visible --blink true

# Set both the success and fail text styles to be bold, underline, and have black backgrounds
$ mnote config style success fail --bold true --underline true --bg black
```
