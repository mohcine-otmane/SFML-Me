import os
import subprocess
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
                             QLineEdit, QMessageBox, QProgressBar, QTextEdit, QFileDialog,
                             QStatusBar, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette


class SFMLProjectGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.project_directory = ""
        self.project_name = ""
        self.project_created = False
        self.project_built = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SFML-ME")
        self.setGeometry(100, 100, 500, 450) # Slightly taller to accommodate status bar

        # Inherit system theme
        self.setStyle(QApplication.style())

        main_layout = QVBoxLayout()  # Main layout for all widgets

        # Project Input Layout
        project_input_layout = QVBoxLayout()
        self.label_name = QLabel("Enter SFML Project Name:")
        project_input_layout.addWidget(self.label_name)

        self.entry_name = QLineEdit()
        self.entry_name.textChanged.connect(self.update_project_name)
        project_input_layout.addWidget(self.entry_name)

        self.label_dir = QLabel("No directory selected")
        project_input_layout.addWidget(self.label_dir)

        main_layout.addLayout(project_input_layout)

        # Log Output Area
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)

        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)


        # Buttons Layout
        buttons_layout = QHBoxLayout()  # Horizontal layout for buttons

        self.btn_select_dir = QPushButton("Select Directory")
        self.btn_select_dir.clicked.connect(self.select_directory)
        buttons_layout.addWidget(self.btn_select_dir)

        self.btn_create = QPushButton("Create Project")
        self.btn_create.clicked.connect(self.create_project)
        self.btn_create.setEnabled(False)  # Disable until directory selected
        buttons_layout.addWidget(self.btn_create)

        self.btn_build = QPushButton("Build Project")
        self.btn_build.clicked.connect(self.build_project)
        self.btn_build.setEnabled(False)  # Disable until project created
        buttons_layout.addWidget(self.btn_build)

        self.btn_run = QPushButton("Run Project")
        self.btn_run.clicked.connect(self.run_project)
        self.btn_run.setEnabled(False)  # Disable until project built
        buttons_layout.addWidget(self.btn_run)

        self.btn_git = QPushButton("Create Git Repo")
        self.btn_git.clicked.connect(self.create_git_repo)
        self.btn_git.setEnabled(False)
        buttons_layout.addWidget(self.btn_git)

        self.btn_clear_log = QPushButton("Clear Log")
        self.btn_clear_log.clicked.connect(self.clear_log)
        buttons_layout.addWidget(self.btn_clear_log)

        main_layout.addLayout(buttons_layout)


        # .gitignore Checkbox (New Feature)
        self.create_gitignore = QPushButton("Create .gitignore")
        self.create_gitignore.setCheckable(True)
        self.create_gitignore.setChecked(True)  # Default to creating it
        main_layout.addWidget(self.create_gitignore)

        # Status Bar (New Feature)
        self.statusbar = QStatusBar()
        main_layout.addWidget(self.statusbar)
        self.statusbar.showMessage("Ready")


        self.setLayout(main_layout)

    def update_project_name(self, text):
        self.project_name = text.strip()
        self.update_button_states()

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.project_directory = directory
            self.log_output.append(f"Selected directory: {directory}")
            self.label_dir.setText(f"Selected directory: {directory}")
            self.update_button_states()
            self.statusbar.showMessage(f"Selected directory: {directory}")
        else:
            QMessageBox.warning(self, "Warning", "No directory selected!")
            self.statusbar.showMessage("Directory selection canceled.")

    def update_button_states(self):
        #Enable buttons based on project state
        has_name = bool(self.project_name)
        has_dir = bool(self.project_directory)

        self.btn_create.setEnabled(has_name and has_dir and not self.project_created)
        self.btn_build.setEnabled(self.project_created)  # Assuming creation means it exists
        self.btn_run.setEnabled(self.project_built)
        self.btn_git.setEnabled(has_dir)  # Assuming creation means it exists

    def clear_log(self):
        self.log_output.clear()

    def _create_directories(self, project_path, directories):
        """Helper function to create directories."""
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)

    def _write_file(self, filepath, content):
        """Helper function to write content to a file."""
        try:
            with open(filepath, "w") as f:
                f.write(content.strip())
        except IOError as e:
            self.log_output.append(f"Error writing to file {filepath}: {e}")
            QMessageBox.critical(self, "Error", f"Failed to write to {filepath}: {e}")
            self.statusbar.showMessage(f"Error writing to file: {e}")
            return False
        return True

    def _create_gitignore(self, project_path):
        """Creates a basic .gitignore file."""
        gitignore_path = os.path.join(project_path, ".gitignore")
        gitignore_content = """
# Build artifacts
build/
*.o
*.exe

# IDE-specific files
.vscode/
*.vcxproj
*.vcxproj.filters
*.sln

# Other
.DS_Store
"""
        return self._write_file(gitignore_path, gitignore_content)


    def create_project(self):
        """Creates the SFML project structure and files."""

        if not self.project_name:
            QMessageBox.critical(self, "Error", "Project name cannot be empty!")
            self.statusbar.showMessage("Project name cannot be empty!")
            return

        if not self.project_directory:
            QMessageBox.critical(self, "Error", "No directory selected!")
            self.statusbar.showMessage("No directory selected!")
            return

        project_path = os.path.join(self.project_directory, self.project_name)

        try:
            self.statusbar.showMessage("Creating project...")

            # Create directories
            directories = ["src", "include", "assets", "build"]
            self._create_directories(project_path, directories)


            # Create files
            files = {
                os.path.join(project_path, "src/main.cpp"): f"""
#include <SFML/Graphics.hpp>
#include "Game.h"
int main() {{
    Game game;
    game.run();
    return 0;
}}
                """,
                os.path.join(project_path, "include/Game.h"): f"""
#ifndef GAME_H
#define GAME_H
#include <SFML/Graphics.hpp>
class Game {{
public:
    Game();
    void run();
private:
    sf::RenderWindow window;
    void processEvents();
    void update();
    void render();
}};
#endif
                """,
                os.path.join(project_path, "src/Game.cpp"): f"""
#include "../include/Game.h"
Game::Game() : window(sf::VideoMode(800, 600), "{self.project_name}") {{}}
void Game::run() {{
    while (window.isOpen()) {{
        processEvents();
        update();
        render();
    }}
}}
void Game::processEvents() {{
    sf::Event event;
    while (window.pollEvent(event)) {{
        if (event.type == sf::Event::Closed)
            window.close();
    }}
}}
void Game::update() {{}}
void Game::render() {{
    window.clear(sf::Color::Black);
    window.display();
}}
                """,
                os.path.join(project_path, "CMakeLists.txt"): f"""
cmake_minimum_required(VERSION 3.10)
project({self.project_name})
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_BUILD_TYPE Release)
find_package(SFML 2.5 COMPONENTS graphics window system REQUIRED)
include_directories(include)
file(GLOB SOURCES "src/*.cpp")
add_executable({self.project_name} ${{SOURCES}})
target_link_libraries({self.project_name} sfml-graphics sfml-window sfml-system)
                """
            }
            success = True
            for filepath, content in files.items():
                if not self._write_file(filepath, content):
                    success = False
                    break

            if success and self.create_gitignore.isChecked():
                success = self._create_gitignore(project_path)

            if success:
                # Initialize Git repository
                subprocess.run(["git", "init", project_path])
                self.log_output.append(f"Project '{self.project_name}' created successfully at {project_path}")
                self.project_created = True
                self.update_button_states() #reenable buttons
                self.statusbar.showMessage(f"Project '{self.project_name}' created successfully!")
            else:
                QMessageBox.critical(self, "Error", f"Project creation failed. See log for details.")
                self.statusbar.showMessage("Project creation failed.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            self.log_output.append(f"An unexpected error occurred: {e}")
            self.statusbar.showMessage(f"An unexpected error occurred: {e}")

    def build_project(self):
        project_name = self.entry_name.text().strip() #this should be gotten from `self.project_name`
        if not project_name or not self.project_directory:
            QMessageBox.critical(self, "Error", "Enter a project name and select a directory!")
            self.statusbar.showMessage("Enter a project name and select a directory!")
            return

        build_dir = os.path.join(self.project_directory, project_name, "build")
        os.makedirs(build_dir, exist_ok=True)

        self.progress.setVisible(True)
        self.progress.setValue(25)
        try:
            self.statusbar.showMessage("Configuring build...")
            process = subprocess.run(["cmake", ".."], cwd=build_dir, capture_output=True, text=True, check=True)
            self.log_output.append(process.stdout + process.stderr)
            self.progress.setValue(50)

            self.statusbar.showMessage("Building project...")
            process = subprocess.run(["cmake", "--build", "."], cwd=build_dir, capture_output=True, text=True, check=True)
            self.log_output.append(process.stdout + process.stderr)
            self.progress.setValue(100)

            QMessageBox.information(self, "Success", "Build completed successfully!")
            self.project_built = True
            self.update_button_states() # Enable run button after successful build
            self.statusbar.showMessage("Build completed successfully!")

        except subprocess.CalledProcessError as e:
            self.progress.setValue(0)
            QMessageBox.critical(self, "Error", f"Build failed!  Error: {e.stderr}")
            self.log_output.append(e.stdout + e.stderr)
            self.project_built = False #ensure project is not built
            self.update_button_states()
            self.statusbar.showMessage(f"Build failed: {e.stderr}")
        finally:
            self.progress.setVisible(False)

    def run_project(self):
        project_name = self.entry_name.text().strip() #this should be gotten from `self.project_name`
        if not project_name or not self.project_directory:
            QMessageBox.critical(self, "Error", "Enter a project name and select a directory!")
            self.statusbar.showMessage("Enter a project name and select a directory!")
            return

        executable_path = os.path.join(self.project_directory, project_name, "build", project_name)
        if not os.path.exists(executable_path):
            QMessageBox.critical(self, "Error", "Executable not found! Build the project first.")
            self.statusbar.showMessage("Executable not found! Build the project first.")
            return

        try:
            self.statusbar.showMessage("Running project...")
            process = subprocess.run(executable_path, capture_output=True, text=True, check=True)
            self.log_output.append(process.stdout + process.stderr)
            self.statusbar.showMessage("Project finished running.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Running project failed!  Error: {e.stderr}")
            self.log_output.append(e.stdout + e.stderr)
            self.statusbar.showMessage(f"Running project failed: {e.stderr}")


    def create_git_repo(self):
        if not self.project_directory:
            QMessageBox.critical(self, "Error", "No directory selected!")
            self.statusbar.showMessage("No directory selected!")
            return

        try:
            self.statusbar.showMessage("Initializing Git repository...")
            process = subprocess.run(["git", "init", self.project_directory], check=True, capture_output=True, text=True)
            self.log_output.append("Initialized a new Git repository in " + self.project_directory)
            self.statusbar.showMessage("Git repository initialized.")
        except subprocess.CalledProcessError as e:
             QMessageBox.critical(self, "Error", f"Git init failed!  Error: {e.stderr}")
             self.log_output.append(e.stdout + e.stderr)
             self.statusbar.showMessage(f"Git init failed: {e.stderr}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply system theme
    app.setStyle("Fusion")  # Or any other available style (e.g., "Windows", "macOS")

    window = SFMLProjectGenerator()
    window.show()
    sys.exit(app.exec())