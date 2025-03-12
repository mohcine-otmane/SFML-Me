from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QProgressBar, QTextEdit, QFileDialog
import subprocess
import os
import sys

class SFMLProjectGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.project_directory = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SFML Project Generator")
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()

        self.label = QLabel("Enter SFML Project Name:")
        layout.addWidget(self.label)

        self.entry = QLineEdit()
        layout.addWidget(self.entry)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        buttons = [
            ("Select Directory", self.select_directory),
            ("Create Project", self.create_project),
            ("Build Project", self.build_project),
            ("Run Project", self.run_project),
            ("Create Git Repo", self.create_git_repo)
        ]

        for text, function in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(function)
            layout.addWidget(btn)

        self.setLayout(layout)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.project_directory = directory
            self.log_output.append(f"Selected directory: {directory}")
        else:
            QMessageBox.warning(self, "Warning", "No directory selected!")

    def create_project(self):
        project_name = self.entry.text().strip()
        if not project_name:
            QMessageBox.critical(self, "Error", "Project name cannot be empty!")
            return
        
        if not self.project_directory:
            QMessageBox.critical(self, "Error", "No directory selected!")
            return

        project_path = os.path.join(self.project_directory, project_name)
        directories = ["src", "include", "assets", "build"]
        for directory in directories:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)

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
Game::Game() : window(sf::VideoMode(800, 600), "{project_name}") {{}}
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
project({project_name})
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_BUILD_TYPE Release)
find_package(SFML 2.5 COMPONENTS graphics window system REQUIRED)
include_directories(include)
file(GLOB SOURCES "src/*.cpp")
add_executable({project_name} ${{SOURCES}})
target_link_libraries({project_name} sfml-graphics sfml-window sfml-system)
            """
        }

        for filepath, content in files.items():
            with open(filepath, "w") as f:
                f.write(content.strip())

        subprocess.run(["git", "init", project_path])
        self.log_output.append(f"Project '{project_name}' created successfully at {project_path}")

    def build_project(self):
        project_name = self.entry.text().strip()
        if not project_name or not self.project_directory:
            QMessageBox.critical(self, "Error", "Enter a project name and select a directory!")
            return

        build_dir = os.path.join(self.project_directory, project_name, "build")
        os.makedirs(build_dir, exist_ok=True)

        self.progress.setVisible(True)
        self.progress.setValue(25)
        process = subprocess.run(["cmake", ".."], cwd=build_dir, capture_output=True, text=True)
        if process.returncode == 0:
            self.progress.setValue(50)
            process = subprocess.run(["cmake", "--build", "."], cwd=build_dir, capture_output=True, text=True)
            if process.returncode == 0:
                self.progress.setValue(100)
                QMessageBox.information(self, "Success", "Build completed successfully!")
            else:
                self.progress.setValue(0)
                QMessageBox.critical(self, "Error", f"Build failed!\n\n{process.stderr}")
        else:
            self.progress.setValue(0)
            QMessageBox.critical(self, "Error", f"CMake configuration failed!\n\n{process.stderr}")

        self.progress.setVisible(False)

    def run_project(self):
        project_name = self.entry.text().strip()
        if not project_name or not self.project_directory:
            QMessageBox.critical(self, "Error", "Enter a project name and select a directory!")
            return

        executable_path = os.path.join(self.project_directory, project_name, "build", project_name)
        if not os.path.exists(executable_path):
            QMessageBox.critical(self, "Error", "Executable not found! Build the project first.")
            return

        subprocess.run(executable_path, shell=True, executable="/bin/bash")

    def create_git_repo(self):
        project_name = self.entry.text().strip()
        if not project_name or not self.project_directory:
            QMessageBox.critical(self, "Error", "Enter a project name and select a directory!")
            return

        project_path = os.path.join(self.project_directory, project_name)
        subprocess.run(["git", "init"], cwd=project_path)
        subprocess.run(["git", "add", "."], cwd=project_path)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=project_path)
        QMessageBox.information(self, "Success", "Git repository initialized!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SFMLProjectGenerator()
    window.show()
    sys.exit(app.exec())
