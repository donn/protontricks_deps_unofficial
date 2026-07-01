import os
import sys
from pathlib import Path

__file_dir__ = Path(__file__).absolute().parent

def winetricks():
    binary_path = __file_dir__ / "winetricks"
    os.execlp("/bin/bash", "bash", binary_path, *sys.argv[1:])

def cabextract():
    binary_path = __file_dir__ / "cabextract"
    os.execlp(binary_path, "cabextract", *sys.argv[1:])
