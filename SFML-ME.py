import os
import subprocess
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
                             QLineEdit, QMessageBox, QProgressBar, QTextEdit, QFileDialog,
                             QStatusBar, QHBoxLayout, QComboBox, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QDesktopServices
from urllib.parse import urlunparse

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
        self.setGeometry(100, 100, 600, 650)  # Adjusted height

        # Inherit system theme
        self.setStyle(QApplication.style())

        main_layout = QVBoxLayout()

        # --- Project Settings Group ---
        project_group = QGroupBox("Project Settings")
        project_layout = QFormLayout()  # Form layout for labels and input fields

        self.label_name = QLabel("Project Name:")
        self.entry_name = QLineEdit()
        self.entry_name.textChanged.connect(self.update_project_name)
        project_layout.addRow(self.label_name, self.entry_name)  # Label to left of input

        self.label_dir = QLabel("Project Directory:")
        self.dir_display = QLabel("No directory selected")
        self.select_dir_btn = QPushButton("Select")
        self.select_dir_btn.clicked.connect(self.select_directory)
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_display)
        dir_layout.addWidget(self.select_dir_btn)
        project_layout.addRow(self.label_dir, dir_layout)

        project_group.setLayout(project_layout)
        main_layout.addWidget(project_group)

        # --- Configuration Group ---
        config_group = QGroupBox("Configuration")
        config_layout = QFormLayout()

        self.sfml_version_label = QLabel("SFML Version:")
        self.sfml_version_combo = QComboBox()
        self.sfml_version_combo.addItems(["2.5", "2.6"])
        self.sfml_version_combo.setCurrentText("2.5")
        config_layout.addRow(self.sfml_version_label, self.sfml_version_combo)

        self.build_type_label = QLabel("Build Type:")
        self.build_type_combo = QComboBox()
        self.build_type_combo.addItems(["Debug", "Release", "RelWithDebInfo", "MinSizeRel"])
        self.build_type_combo.setCurrentText("Release")
        config_layout.addRow(self.build_type_label, self.build_type_combo)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # --- Progress Bar (moved above Actions) ---
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setVisible(False)
        main_layout.addWidget(self.progress)  # Add the progress bar to the main layout BEFORE actions


        # --- Actions Group ---
        action_group = QGroupBox("Actions")
        action_layout = QHBoxLayout()  # hlayout


        self.btn_create = QPushButton("Create Project")
        self.btn_create.clicked.connect(self.create_project)
        self.btn_create.setEnabled(False)

        self.btn_build = QPushButton("Build Project")
        self.btn_build.clicked.connect(self.build_project)
        self.btn_build.setEnabled(False)

        self.btn_run = QPushButton("Run Project")
        self.btn_run.clicked.connect(self.run_project)
        self.btn_run.setEnabled(False)

        action_layout.addWidget(self.btn_create)
        action_layout.addWidget(self.btn_build)
        action_layout.addWidget(self.btn_run)

        action_group.setLayout(action_layout)
        main_layout.addWidget(action_group)


        # --- More Actions Group ---
        extra_group = QGroupBox("Extra Actions")
        extra_layout = QHBoxLayout()

        self.btn_git = QPushButton("Create Git Repo")
        self.btn_git.clicked.connect(self.create_git_repo)
        self.btn_git.setEnabled(False)

        self.create_gitignore = QPushButton("Create .gitignore")
        self.create_gitignore.setCheckable(True)
        self.create_gitignore.setChecked(True)

        self.btn_open_editor = QPushButton("Open in VS Code")
        self.btn_open_editor.clicked.connect(self.open_in_editor)
        self.btn_open_editor.setEnabled(False)

        extra_layout.addWidget(self.btn_git)
        extra_layout.addWidget(self.create_gitignore)
        extra_layout.addWidget(self.btn_open_editor)

        extra_group.setLayout(extra_layout)
        main_layout.addWidget(extra_group)


        # --- Log and Clean ---
        log_layout = QHBoxLayout()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        self.btn_clear_log = QPushButton("Clear Log")
        self.btn_clear_log.clicked.connect(self.clear_log)

        log_layout.addWidget(self.log_output)
        log_layout.addWidget(self.btn_clear_log)

        main_layout.addLayout(log_layout)


        # Status Bar
        self.statusbar = QStatusBar()
        main_layout.addWidget(self.statusbar)
        self.statusbar.showMessage("Ready")

        self.setLayout(main_layout)


    def _generate_main_cpp(self):
        """Generates the content for main.cpp"""
        return f"""
#include <SFML/Graphics.hpp>
#include "Game.h"
int main() {{
    Game game;
    game.run();
    return 0;
}}
                """

    def _generate_game_h(self):
      """Generates the content for Game.h"""
      return f"""
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
            """
    def _generate_game_cpp(self):
      """Generates the content for Game.cpp"""
      return f"""
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
            """

    def _generate_cmakelists_txt(self):
        """Generates the content for CMakeLists.txt"""
        cmake_version_required = self.get_cmake_minimum_required()
        return f"""
cmake_minimum_required(VERSION {cmake_version_required})
project({self.project_name})
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_BUILD_TYPE ${{CMAKE_BUILD_TYPE}})
set(SFML_VERSION {self.sfml_version_combo.currentText()})
find_package(SFML ${{SFML_VERSION}} COMPONENTS graphics window system REQUIRED)
include_directories(include)
file(GLOB SOURCES "src/*.cpp")
add_executable({self.project_name} ${{SOURCES}})
target_link_libraries({self.project_name} sfml-graphics sfml-window sfml-system)
                """

    def update_project_name(self, text):
        self.project_name = text.strip()
        self.update_button_states()

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if directory:
            self.project_directory = directory
            self.log_output.append(f"Selected directory: {directory}")
            self.dir_display.setText(directory) #set label path on gui next to button
            self.update_button_states()
            self.statusbar.showMessage(f"Selected directory: {directory}")
        else:
            QMessageBox.warning(self, "Warning", "No directory selected!")
            self.statusbar.showMessage("Directory selection canceled.")

    def update_button_states(self):
        has_name = bool(self.project_name)
        has_dir = bool(self.project_directory)
        self.btn_create.setEnabled(has_name and has_dir and not self.project_created)
        self.btn_build.setEnabled(self.project_created)
        self.btn_run.setEnabled(self.project_built)
        self.btn_git.setEnabled(has_dir)
        self.btn_open_editor.setEnabled(self.project_created)

    def clear_log(self):
        self.log_output.clear()

    def _create_directories(self, project_path, directories):
        for directory in directories:
            self.statusbar.showMessage(f"Creating Directory: {directory}...")
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)

    def _write_file(self, filepath, content):
        try:
            self.statusbar.showMessage(f"Writing file: {filepath}...")
            with open(filepath, "w") as f:
                f.write(content.strip())
            return True
        except IOError as e:
            self.log_output.append(f"Error writing to file {filepath}: {e}")
            QMessageBox.critical(self, "Error", f"Failed to write to {filepath}: {e}")
            self.statusbar.showMessage(f"Error writing to file: {e}")
            return False

    def _append_gitignore(self, project_path):
        """Appends a .gitignore file to any existing one."""

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

        try:
            if os.path.exists(gitignore_path):
              with open(gitignore_path, "a") as f:  # Append mode
                  f.write(gitignore_content.strip())
            else:
              with open(gitignore_path, "w") as f:  # Create a new one if not available.
                  f.write(gitignore_content.strip())

            self.statusbar.showMessage(".gitignore created/updated successfully!")
            return True

        except IOError as e:
          self.log_output.append(f"Error writing/appending to .gitignore: {e}")
          QMessageBox.critical(self, "Error", f"Failed to write to .gitignore: {e}")
          self.statusbar.showMessage(f"Failed to write/append to .gitignore: {e}") # Update status bar.
          return False


    def get_cmake_minimum_required(self):
      return "3.10"


    def create_project(self):
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
            self.statusbar.showMessage("Creating project directories...")
            directories = ["src", "include", "assets", "build"]
            self._create_directories(project_path, directories)


            files = {
                os.path.join(project_path, "src/main.cpp"): self._generate_main_cpp(),
                os.path.join(project_path, "include/Game.h"): self._generate_game_h(),
                os.path.join(project_path, "src/Game.cpp"): self._generate_game_cpp(),
                os.path.join(project_path, "CMakeLists.txt"): self._generate_cmakelists_txt(),
            }
            success = True
            for filepath, content in files.items():
                if not self._write_file(filepath, content):
                    success = False
                    break


            if success and self.create_gitignore.isChecked():
                success = self._append_gitignore(project_path)


            if success:
                self.statusbar.showMessage("Initializing Git Repository")
                subprocess.run(["git", "init", project_path])
                self.log_output.append(f"Project '{self.project_name}' created successfully at {project_path}")
                self.project_created = True
                self.update_button_states() #reenable buttons
                self.statusbar.showMessage(f"Project '{self.project_name}' created successfully!") #Overall Success
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
            cmake_command = ["cmake", "..", f"-DCMAKE_BUILD_TYPE={self.build_type_combo.currentText()}"] # Pass build type
            process = subprocess.run(cmake_command, cwd=build_dir, capture_output=True, text=True, check=True)
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

    def open_in_editor(self):
        """Opens the project directory in VS Code."""
        if not self.project_directory or not self.project_name:
            QMessageBox.critical(self, "Error", "Project directory or name not set.")
            self.statusbar.showMessage("Project directory or name not set.")
            return

        project_path = os.path.join(self.project_directory, self.project_name)
        editor_command = ["code", project_path]  # HARDCODED vcode regardless
        try:
            subprocess.run(editor_command, check=True) #Still use vscode always hardcode always
            self.statusbar.showMessage("Opened project in VS Code.")
        except FileNotFoundError:
            QMessageBox.warning(self, "Warning", f"VS Code not found. Make sure it's installed and in your PATH.")
            self.statusbar.showMessage(f"VS Code is always needed!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error opening in editor: {e}")
            self.statusbar.showMessage(f"Error opening in editor: {e}")


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
    app.setStyle("Fusion")

    window = SFMLProjectGenerator()
    window.show()
    sys.exit(app.exec())