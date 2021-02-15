# Design Ideas and Documentation


## Indicies

### General idea 

The general idea is to have notes in repos, each of which is mapped by an index. A global index joins all of them together.

A singular index maps to a single directory and contains everything in all of its subfolders.

The index would basically hold three(?) things:

1. A list of file information consisting of file names, paths, last modified timestamp, file size, and potentially a checksum
2. Known notes in the index directory, including metadata about them.
3. A bi-directional(?) mapping between files and notes

### Principle

The principle of the index is to cache information about the notes so that they do not need to be completely reloaded every time the program runs. Data can be guessed at whether it's valid by either comparing timestamp and last modified date (like rsync) or checksums.

### Global Index
The global index is a parent to each index. Its data is stored in the configuration folder and is a simple yaml configuration file with a list key/value pairs where the key is the index name and the value is a dictionary containing properties (currently just the path)

Loading all of the indices involves loading them all in order, but building a master ID index that is checked against when each note is loaded. Notes that conflict must be marked as conflicting somehow.

### Construction
The index is initially constructable from the data in the folder.  If the index data is lost or destroyed it should be possible to competely rebuild it.

The initial construction should involve recursively finding all markdown files in the folder. Then checksums are computed and the file information is stored.

Next, all of the files are loaded based on their information and the loading of the note metadata is attempted. This can have three results:
1. The metadata loaded successfully
2. There was a spot for metadata but it failed to load (corrupted?)
3. There was no metadata in the file

If the metadata loads, it may or may not have an ID. IDs are required for global uniquness.

As the metadata loads IDs must be checked against the global list.  IDs that are duplicated need to be marked as conflicts and resolved before these notes can be fully added to the index.

The ID state for each not can be:
1. Has no ID
2. Has a conflicting ID
3. Has a unique ID

### When the program runs

When the program runs and intends to run an operation which involves the index, it will first need to discover which index it is inside.

Then it will need to determine the differences between the index and the reality of directory contents.

#### Differencing

All actual file information needs to be captured from the directory, but not opened (unless the checksum method is being used).

The differences involve:
1. Actual files that are not in the index (new files or moved files)
2. Index files that are not in the actual files (deleted files or moved files)
3. Actual files whose contents have likely changed since the index was constructed

Index files which have not been mapped to an actual file should be removed first. This prevents conflicts from occurring if it just turns out that the file has moved.

Actual files which are not in the index need to be merged into the index.  This involves the same process as building the index (building is effectively merging notes into an index that starts empty).

Then files who do not match parameters (either timestamp+size or checksum) should be removed from the index and recreated.

### Adding a new index

When adding a new index, the main danger is duplicating IDs. We can run through the creation process but must have a means of resolving ID conflicts.

---

## Other Future Ideas

#### Backlinks

Probably would be helped by functioning indices first in order to have a global view of the search for links

#### Backups

Quick means of moving all markdown files into place for archival/revision control

* To a git repository
* Pack and zip

#### UUID or SHA1 Resources 

Rename all resources with uuids or content shas in order to decouple them from their file paths.

