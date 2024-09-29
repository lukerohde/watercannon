# auto_test.py

import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from pathlib import Path
import sys

# Manually configure additional mappings here
manual_test_mapping = {
    # 'src/module_extra.py': 'tests/test_module_extra.py',
}

def preload_test_mapping(project_root, manual_mapping):
    mapping = manual_mapping.copy()
    source_dir = project_root
    tests_dir = project_root / 'tests'

    for source_file in source_dir.glob('*.py'):
        if source_file.name.startswith('test_'):
            continue  # Skip test files in the root directory if any
        test_file = tests_dir / f'test_{source_file.name}'
        if test_file.exists():
            mapping[str(source_file.relative_to(project_root))] = str(test_file.relative_to(project_root))
    
    return mapping

class TestRunnerHandler(FileSystemEventHandler):
    def __init__(self, test_mapping, project_root):
        self.test_mapping = test_mapping
        self.project_root = Path(project_root).resolve()  # Ensure project root is absolute

    def run_all_tests(self):
        print('\nRunning all tests...')
        subprocess.run(['python', '-m', 'unittest', 'discover', '-s', 'tests'])
        print('All tests completed.\n')

    def on_modified(self, event):
        changed_path = Path(event.src_path).resolve()
        if not changed_path.suffix == '.py':
            return  # Ignore non-Python files

        try:
            relative_path = changed_path.relative_to(self.project_root)
        except ValueError:
            # The changed file is not inside the project root
            return

        print(f'Change detected in {relative_path}.')
        
        if relative_path.parent == Path('tests') and relative_path.name.startswith('test_'):
            # If a test file is modified, run that specific test
            subprocess.run(['python', '-m', 'unittest', str(relative_path)])
        elif relative_path.parent == Path('tests'):
            # If other files in tests are modified, run all tests
            self.run_all_tests()
        else:
            # If a source file is modified, find and run its corresponding test
            test_file_str = self.test_mapping.get(str(relative_path))
            if test_file_str and (self.project_root / test_file_str).exists():
                test_file = Path(test_file_str)
                print(f'Running tests in "{test_file}"...')
                subprocess.run(['python', '-m', 'unittest', str(test_file)])
            else:
                # If no specific test is found, run all tests
                print(f'Not sure what to do.')
                self.run_all_tests()

def main():
    project_root = '.'  # Define the project root directory

    # Initialize the test runner handler
    test_mapping = preload_test_mapping(Path(project_root), manual_test_mapping)
    event_handler = TestRunnerHandler(test_mapping, project_root)
    observer = Observer()
    observer.schedule(event_handler, path=project_root, recursive=True)
    observer.start()

    event_handler.run_all_tests()
    print('Watching for changes...')

    try:
        while True:
            print('Press ENTER to run all tests manually.')
            user_input = input()
            event_handler.run_all_tests()
    except KeyboardInterrupt:
        print('\nStopping observer...')
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()