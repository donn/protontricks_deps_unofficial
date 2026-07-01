
# Copyright (C) 2026 Mohamed Gaber <me@donn.website>
#
# Adapted from Yosys
#
# Copyright (C) 2026 Catherine <whitequark@whitequark.org>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
import os
import sys
import hashlib
import certifi
import pathlib
import tarfile
import tempfile
import sysconfig
import subprocess
import urllib.request
from email.policy import EmailPolicy
from email.message import EmailMessage
from wheel.wheelfile import WheelFile

PROJECT_NAME = "protontricks_deps_unofficial"
PROJECT_VERSION = "2026.01.25"  # match winetricks
DIST_NAME = f"{PROJECT_NAME}-{PROJECT_VERSION}"

WINETRICKS_URL = "https://raw.githubusercontent.com/Winetricks/winetricks/refs/tags/20260125/src/winetricks"
WINETRICKS_SHA256 = "431f82fc74000e6c864409f1d8fb495d696c03928808e3e8acffc45179312a7b"
CABEXTRACT_URL = "https://www.cabextract.org.uk/cabextract-1.11.tar.gz"
CABEXTRACT_SHA256 = "b5546db1155e4c718ff3d4b278573604f30dd64c3c5bfd4657cd089b823a3ac6"

ENTRY_POINTS = f"""
[console_scripts]
winetricks = {PROJECT_NAME}.wrapper:winetricks
cabextract = {PROJECT_NAME}.wrapper:cabextract
"""

if sys.implementation.name == "cpython":
    PYTHON_TAG = f"cp{sysconfig.get_config_var('py_version_nodot')}"
    # freethreaded builds have an ABI flag appended, "t"
    ABI_TAG = f"cp{sysconfig.get_config_var('py_version_nodot')}{sysconfig.get_config_var('abiflags')}"
else:
    raise NotImplementedError("unsupported Python implementation")

PLATFORM_TAG_RAW = sysconfig.get_platform()
PLATFORM_TAG = (
    PLATFORM_TAG_RAW.lower().replace("-", "_").replace(".", "_").replace(" ", "_")
)
COMPAT_TAG = f"{PYTHON_TAG}-{ABI_TAG}-{PLATFORM_TAG}"


def make_message(headers, payload=None):
    msg = EmailMessage(policy=EmailPolicy(max_line_length=0))
    for name, value in headers:
        if isinstance(value, list):
            for value_part in value:
                msg[name] = value_part
        else:
            msg[name] = value
    if payload:
        msg.set_payload(payload)
    return bytes(msg)


def build_sdist(sdist_dir, config_settings=None):
    sdist_filename = f"{DIST_NAME}.tar.gz"

    with tarfile.open(
        pathlib.Path(sdist_dir) / sdist_filename,
        "w:gz",
        format=tarfile.PAX_FORMAT,
    ) as sdist:

        def exclude_build(entry):
            name = entry.name.removeprefix(f"{DIST_NAME}/")
            if name in (".cache", "build", "dist", "venv"):
                return
            if os.path.basename(name) in (".git", "__pycache__"):
                return
            return entry

        sdist.add(os.getcwd(), arcname=DIST_NAME, filter=exclude_build)

    return sdist_filename


def get_metadata_files():
    with open("README.md", "rb") as readme:
        long_description = readme.read()

    return {
        "WHEEL": make_message(
            [
                ("Wheel-Version", "1.0"),
                ("Generator", "steamdeck tricks metapackage build backend"),
                ("Root-Is-Purelib", "false"),
                ("Tag", [COMPAT_TAG]),
            ]
        ),
        "METADATA": make_message(
            [
                ("Metadata-Version", "2.4"),
                ("Name", PROJECT_NAME),
                ("Version", PROJECT_VERSION),
                (
                    "Summary",
                    "Unofficial collection for binary dependencies for protontricks for immutable GNU/Linux distributions",
                ),
                ("Description-Content-Type", "text/markdown"),
                ("Classifier", "Programming Language :: Python :: 3"),
                ("Classifier", "Operating System :: POSIX :: Linux"),
                ("Requires-Python", ">=3.10"),
            ],
            long_description,
        ),
        "entry_points.txt": ENTRY_POINTS.encode("utf8"),
    }


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    os.mkdir(f"{metadata_directory}/{DIST_NAME}.dist-info")

    for filename, contents in get_metadata_files().items():
        with open(f"{metadata_directory}/{DIST_NAME}.dist-info/{filename}", "wb") as f:
            f.write(contents)

    return f"{DIST_NAME}.dist-info"


def build_wheel(wheel_dir, config_settings=None, metadata_directory=None):
    wheel_filename = f"{DIST_NAME}-{COMPAT_TAG}.whl"

    with WheelFile(pathlib.Path(wheel_dir) / wheel_filename, "w") as wheel:
        for filename, contents in get_metadata_files().items():
            wheel.writestr(f"{DIST_NAME}.dist-info/{filename}", contents)

        cmake_options = []
        if config_settings is not None:
            if cmake_options := config_settings.get("cmake", cmake_options):
                if isinstance(cmake_options, str):
                    cmake_options = [cmake_options]

        os.environ["SSL_CERT_FILE"] = certifi.where()

        with tempfile.TemporaryDirectory(f".{PROJECT_NAME}-build", "w") as d_str:
            d = pathlib.Path(d_str)

            # python
            wheel.write(f"{PROJECT_NAME}/wrapper.py")

            # winetricks
            urllib.request.urlretrieve(WINETRICKS_URL, d / "winetricks")
            wheel.write(d / "winetricks", f"{PROJECT_NAME}/winetricks")
            with open(d / "winetricks", "rb") as f:
                got = hashlib.file_digest(f, "sha256").hexdigest()
                assert (
                    WINETRICKS_SHA256 == got
                ), f"upstream hash for winetricks changed: {got}"

            # cabextract
            urllib.request.urlretrieve(CABEXTRACT_URL, d / "cabextract-src.tar.gz")

            def strip_first_component(member, path):
                if tarfile.data_filter(member, path) is None:
                    return None
                member.name = str(pathlib.Path(*pathlib.Path(member.name).parts[1:]))
                return member

            with tarfile.open(d / "cabextract-src.tar.gz", mode="r:gz") as tf:
                tf.extractall(d / "cabextract", filter=strip_first_component)
            with open(d / "cabextract-src.tar.gz", "rb") as f:
                got = hashlib.file_digest(f, "sha256").hexdigest()
                assert (
                    CABEXTRACT_SHA256 == got
                ), f"upstream hash for cabextract source changed: {got}"

            subprocess.check_call(
                ["bash", d / "cabextract" / "configure"],
                cwd=d / "cabextract",
            )
            subprocess.check_call(
                ["make", f"-j{os.cpu_count()}"],
                cwd=d / "cabextract",
            )
            wheel.write(
                d / "cabextract" / "cabextract",
                f"{PROJECT_NAME}/cabextract",
            )

    return wheel_filename
