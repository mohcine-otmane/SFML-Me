from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, QProgressBar
import subprocess
import os
import sys

class SFMLProjectGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SFML Project Generator")
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()

        self.label = QLabel("Enter SFML Project Name:")
        layout.addWidget(self.label)

        self.entry = QLineEdit()
        layout.addWidget(self.entry)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        buttons = [
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

    def create_project(self):
        project_name = self.entry.text().strip()
        if not project_name:
            QMessageBox.critical(self, "Error", "Project name cannot be empty!")
            return

        directories = ["src", "include", "assets", "build"]
        for directory in directories:
            os.makedirs(f"{project_name}/{directory}", exist_ok=True)

        files = {
            f"{project_name}/src/main.cpp": f"""
#include <SFML/Graphics.hpp>
#include "Game.h"
int main() {{
    Game game;
    game.run();
    return 0;
}}
            """,
            f"{project_name}/include/Game.h": f"""
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
            f"{project_name}/src/Game.cpp": f"""
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
            f"{project_name}/CMakeLists.txt": f"""
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

        subprocess.run(["git", "init", project_name])
        QMessageBox.information(self, "Success", f"Project '{project_name}' created successfully!")

    def build_project(self):
        project_name = self.entry.text().strip()
        if not project_name:
            QMessageBox.critical(self, "Error", "Enter a project name first!")
            return
        
        build_dir = f"{project_name}/build"
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
        if not project_name:
            QMessageBox.critical(self, "Error", "Enter a project name first!")
            return
        
        executable_path = f"./{project_name}/build/{project_name}"
        if not os.path.exists(executable_path):
            QMessageBox.critical(self, "Error", "Executable not found! Build the project first.")
            return
        
        subprocess.run(executable_path, shell=True, executable="/bin/bash")

    def create_git_repo(self):
        project_name = self.entry.text().strip()
        if not project_name:
            QMessageBox.critical(self, "Error", "Enter a project name first!")
            return
        
        if not os.path.exists(project_name):
            QMessageBox.critical(self, "Error", "Project does not exist. Create it first!")
            return
        
        subprocess.run(["git", "init"], cwd=project_name)
        subprocess.run(["git", "add", "."], cwd=project_name)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=project_name)
        QMessageBox.information(self, "Success", "Git repository initialized!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SFMLProjectGenerator()
    window.show()
    sys.exit(app.exec())