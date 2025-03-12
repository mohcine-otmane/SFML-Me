import os
import subprocess
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
                             QLineEdit, QMessageBox, QProgressBar, QTextEdit, QFileDialog)
from PyQt6.QtCore import Qt

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
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()

        self.label_name = QLabel("Enter SFML Project Name:")
        layout.addWidget(self.label_name)

        self.entry_name = QLineEdit()
        self.entry_name.textChanged.connect(self.update_project_name)
        layout.addWidget(self.entry_name)

        self.label_dir = QLabel("No directory selected")
        layout.addWidget(self.label_dir)


        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.btn_select_dir = QPushButton("Select Directory")
        self.btn_select_dir.clicked.connect(self.select_directory)
        layout.addWidget(self.btn_select_dir)


        self.btn_create = QPushButton("Create Project")
        self.btn_create.clicked.connect(self.create_project)
        self.btn_create.setEnabled(False)  # Disable until directory selected
        layout.addWidget(self.btn_create)

        self.btn_build = QPushButton("Build Project")
        self.btn_build.clicked.connect(self.build_project)
        self.btn_build.setEnabled(False)  # Disable until project created
        layout.addWidget(self.btn_build)

        self.btn_run = QPushButton("Run Project")
        self.btn_run.clicked.connect(self.run_project)
        self.btn_run.setEnabled(False)  # Disable until project built
        layout.addWidget(self.btn_run)

        self.btn_git = QPushButton("Create Git Repo")
        self.btn_git.clicked.connect(self.create_git_repo)
        self.btn_git.setEnabled(False)
        layout.addWidget(self.btn_git)


        self.setLayout(layout)

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
        else:
            QMessageBox.warning(self, "Warning", "No directory selected!")

    def update_button_states(self):
        #Enable buttons based on project state
        has_name = bool(self.project_name)
        has_dir = bool(self.project_directory)
        #project_exists = False # Add a check if project already created

        self.btn_create.setEnabled(has_name and has_dir and not self.project_created)
        self.btn_build.setEnabled(self.project_created)  # Assuming creation means it exists
        self.btn_run.setEnabled(self.project_built)
        self.btn_git.setEnabled(has_dir)  # Assuming creation means it exists


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
            return False
        return True

    def create_project(self):
        """Creates the SFML project structure and files."""

        if not self.project_name:
            QMessageBox.critical(self, "Error", "Project name cannot be empty!")
            return

        if not self.project_directory:
            QMessageBox.critical(self, "Error", "No directory selected!")
            return

        project_path = os.path.join(self.project_directory, self.project_name)

        try:
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


            if success:
                # Initialize Git repository
                subprocess.run(["git", "init", project_path])
                self.log_output.append(f"Project '{self.project_name}' created successfully at {project_path}")
                self.project_created = True
                self.update_button_states() #reenable buttons
            else:
                QMessageBox.critical(self, "Error", f"Project creation failed. See log for details.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            self.log_output.append(f"An unexpected error occurred: {e}")

    def build_project(self):
        project_name = self.entry_name.text().strip() #this should be gotten from `self.project_name`
        if not project_name or not self.project_directory:
            QMessageBox.critical(self, "Error", "Enter a project name and select a directory!")
            return

        build_dir = os.path.join(self.project_directory, project_name, "build")
        os.makedirs(build_dir, exist_ok=True)

        self.progress.setVisible(True)
        self.progress.setValue(25)
        try:
            process = subprocess.run(["cmake", ".."], cwd=build_dir, capture_output=True, text=True, check=True)
            self.log_output.append(process.stdout + process.stderr)
            self.progress.setValue(50)
            process = subprocess.run(["cmake", "--build", "."], cwd=build_dir, capture_output=True, text=True, check=True)
            self.log_output.append(process.stdout + process.stderr)
            self.progress.setValue(100)
            QMessageBox.information(self, "Success", "Build completed successfully!")
            self.project_built = True
            self.update_button_states() # Enable run button after successful build
        except subprocess.CalledProcessError as e:
            self.progress.setValue(0)
            QMessageBox.critical(self, "Error", f"Build failed!  Error: {e.stderr}")
            self.log_output.append(e.stdout + e.stderr)
            self.project_built = False #ensure project is not built
            self.update_button_states()
        finally:
            self.progress.setVisible(False)

    def run_project(self):
        project_name = self.entry_name.text().strip() #this should be gotten from `self.project_name`
        if not project_name or not self.project_directory:
            QMessageBox.critical(self, "Error", "Enter a project name and select a directory!")
            return

        executable_path = os.path.join(self.project_directory, project_name, "build", project_name)
        if not os.path.exists(executable_path):
            QMessageBox.critical(self, "Error", "Executable not found! Build the project first.")
            return

        try:
            process = subprocess.run(executable_path, capture_output=True, text=True, check=True)
            self.log_output.append(process.stdout + process.stderr)
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Running project failed!  Error: {e.stderr}")
            self.log_output.append(e.stdout + e.stderr)


    def create_git_repo(self):
        if not self.project_directory:
            QMessageBox.critical(self, "Error", "No directory selected!")
            return

        try:
            subprocess.run(["git", "init", self.project_directory], check=True, capture_output=True, text=True)
            self.log_output.append("Initialized a new Git repository in " + self.project_directory)
        except subprocess.CalledProcessError as e:
             QMessageBox.critical(self, "Error", f"Git init failed!  Error: {e.stderr}")
             self.log_output.append(e.stdout + e.stderr)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SFMLProjectGenerator()
    window.show()
    sys.exit(app.exec())