# SFML-ME

SFML-ME is a Qt-based project generator for SFML C++ games. It automates project setup, compilation, and execution using CMake, streamlining game development. The project features a Python-based GUI built with PyQt6 for easy interaction.

## Features
- **Project Creation:** Generates a structured SFML project with source, headers, assets, and build directories.
- **CMake Integration:** Automatically configures a CMake-based build system.
- **Build & Run:** Compile and execute projects with a simple button click.
- **Git Repository Setup:** Initializes a Git repository and commits the initial files.
- **GUI Interface:** Built using PyQt6 for a user-friendly experience.
- **Progress Indicator:** Displays build progress dynamically.

## Installation
### Prerequisites
Ensure you have the following installed:
- CMake
- SFML (Simple and Fast Multimedia Library)
- g++ (or another C++ compiler)
- Python3
- PyQt6 (`pip install PyQt6`)

### Setup
Clone the repository and navigate to the project directory:
```sh
git clone https://github.com/your-username/SFML-ME.git
cd SFML-ME
```
Run the Python GUI script:
```sh
python3 SFML_Game_Template.py
```

## Usage
1. Enter a project name and click "Create Project".
2. Click "Build Project" to compile the game.
3. Click "Run Project" to execute the game.
4. Click "Create Git Repo" to initialize version control.

## Project Structure
```
SFML-ME/
│-- SFML_Game_Template.py  # Main GUI script
│-- src/
│   ├── main.cpp  # Entry point
│   ├── Game.cpp  # Game logic
│-- include/
│   ├── Game.h  # Game class header
│-- assets/  # Placeholder for game assets
│-- build/  # Compiled binaries and CMake build files
│-- CMakeLists.txt  # CMake configuration
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss the proposed changes.

## Author
Developed by Mohcine Otmane. Feel free to reach out for suggestions or improvements!

