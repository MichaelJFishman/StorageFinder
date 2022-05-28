import os
from typing import List
from pathlib import Path

home_dir = Path.home()


def format_bytes(size):
    """
    from https://stackoverflow.com/a/49361727
    """
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 3)} {power_labels[n]}"


class Folder:
    subdirs: List["Folder"]
    def __init__(self, pth):
        self.pth = pth

        self.subdirs = []
        self.filenames = []
        for nm in os.listdir(self.pth):
            pth_ = f"{self.pth}/{nm}"
            if os.path.isfile(pth_):
                self.filenames.append(nm)
            elif os.path.isdir(pth_):
                self.subdirs.append(Folder(pth_))

        self._size_flat = None
        self._size_recursive = None

    @property
    def size_flat(self):
        if self._size_flat is None:
            size = 0
            for nm in self.filenames:
                pth = f"{self.pth}/{nm}"
                if not os.path.islink(pth):
                    size += os.path.getsize(pth)
            self._size_flat = size
        return self._size_flat

    @property
    def size_recursive(self):
        if self._size_recursive is None:
            size = self.size_flat
            for dir in self.subdirs:
                size += dir.size_recursive
            self._size_recursive = size
        return self._size_recursive

    def print_sizes(self, min_size = 1000000000):
        lines = []
        lines.append(f"{self.pth} -- {format_bytes(self.size_recursive)}")
        for nm in self.filenames:
            # It would be more efficient to store filesizes the first time we call getsize
            fp = f"{self.pth}/{nm}"
            filesize = os.path.getsize(fp)
            if filesize >= min_size:
                lines.append(f"\t{nm} -- {format_bytes(filesize)}")
        for sd in self.subdirs:
            if sd.size_recursive >= min_size:
                s = sd.print_sizes(min_size=min_size)
                s = s.replace("\n", "\n\t")
                lines.append(s)
        return "\n".join(lines)
    
    



if __name__ == "__main__":
    root_folder = Folder(f"{home_dir}/Documents")
    s = root_folder.print_sizes(min_size=1000000000)
    out_pth = f"results/Documents.txt"
    os.makedirs(os.path.dirname(out_pth), exist_ok=True)
    with open(out_pth, "w") as f:
        f.write(s)