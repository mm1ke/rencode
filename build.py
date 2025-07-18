from __future__ import annotations

import os
import shutil

from pathlib import Path

from Cython.Build import cythonize
from setuptools import Distribution
from setuptools import Extension
from setuptools.command.build_ext import build_ext

LINK_ARGS: list[str] = []
INCLUDE_DIRS: list[str] = []
LIBRARIES: list[str] = []


def build() -> None:
    extensions = [
        Extension(
            "*",
            ["rencode/*.pyx"],
            extra_link_args=LINK_ARGS,
            include_dirs=INCLUDE_DIRS,
            libraries=LIBRARIES,
        )
    ]
    ext_modules = cythonize(
        extensions,
        include_path=INCLUDE_DIRS,
        compiler_directives={"binding": True, "language_level": 3},
    )

    distribution = Distribution({
        "name": "rencode",
        "ext_modules": ext_modules
    })

    cmd = build_ext(distribution)
    cmd.ensure_finalized()
    cmd.run()

    # Copy built extensions back to the project
    for output in cmd.get_outputs():
        output = Path(output)
        relative_extension = output.relative_to(cmd.build_lib)
        for so in relative_extension.parent.glob('*.so'):
            so.unlink()
        shutil.copyfile(output, relative_extension)
        mode = os.stat(relative_extension).st_mode
        mode |= (mode & 0o444) >> 2
        os.chmod(relative_extension, mode)


if __name__ == "__main__":
    build()
