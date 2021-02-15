import time
import random
import uuid
from mnotes.utility.file_system import FileInfo

_n_runs = 1_000_000
_n_corpus = 10_000


def perf_file_info_to_dict():
    # Generate FileInfo
    infos = []
    for n in range(_n_runs):
        infos.append(FileInfo("/this/test/file", "note.md",
                              random.random(), random.randint(1, 100_000), uuid.uuid4().hex))

    start = time.time()
    dicts = [i.to_dict() for i in infos]
    end = time.time()
    each = (end - start) / _n_runs
    print(f"To dictionary: {each * 1000.0:0.3f}ms each, {each * _n_corpus:0.3f}s for est corpus")


if __name__ == '__main__':
    perf_file_info_to_dict()