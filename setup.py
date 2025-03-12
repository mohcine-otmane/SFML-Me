from setuptools import setup, find_packages
from SFMLME import __version__


setup(
    name="sfml-me",
    version=__version__,
    author="Mohcine Otmane",
    description="A tool to easily set up SFML projects with CMake and Git integration.",
    packages=find_packages(),
    install_requires=[
        "PyQt6"
    ],
    entry_points={
        "gui_scripts": [
            "sfml-me = sfml_me:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
