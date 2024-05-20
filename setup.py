from setuptools import setup

import hexagon.__init__ as meta

import os

os.system("cp -r ./.hexagon/ ~/")

setup(
    name="hexagon",
    version=meta.__version__,
    description="一个对codeforces polygon的拙劣模仿",
    entry_points={"console_scripts": ["hexagon = hexagon.hexagon:main"]},
    url="https://github.com/LucidaLu/hexagon",
    author="LucidaLu",
    author_email="luyiren12@gmail.com",
    license="MIT",
    packages=["hexagon"],
    install_requires=["pandas", "psutil", "PyYAML", "tqdm","markdown"],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
    ],
)
