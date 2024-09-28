# auto_test.py

import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from pathlib import Path

# o1-mini: Manually configure additional mappings here
manual_test_mapping = {
    # 'src/module_extra.py': 'tests/test_module_extra.py',
}

def preload_test_mapping(project_root, manual_mapping):
    """
    Preload test mappings by scanning the project for source and test files.

    Args:
        project_root (Path): The root directory of the project.
        manual_mapping (dict): Manually configured test mappings.

    Returns:
        dict: Combined test mappings.
    """
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
        self.project_root = Path(project_root).resolve()  # o1-mini: Ensure project root is absolute

    def on_modified(self, event):
        changed_path = Path(event.src_path).resolve()
        if not changed_path.suffix == '.py':
            return  # o1-mini: Ignore non-Python files

        try:
            relative_path = changed_path.relative_to(self.project_root)
        except ValueError:
            # The changed file is not inside the project root
            return

        print(f'Change detected in {relative_path}. Running related tests...')
        
        if relative_path.parent == Path('tests') and relative_path.name.startswith('test_'):
            # o1-mini: If a test file is modified, run that specific test
            subprocess.run(['python', '-m', 'unittest', str(relative_path)])
        elif relative_path.parent == Path('tests'):
            # o1-mini: If other files in tests are modified, run all tests
            subprocess.run(['python', '-m', 'unittest', 'discover', '-s', 'tests'])
        else:
            # o1-mini: If a source file is modified, find and run its corresponding test
            test_file = Path(self.test_mapping.get(str(relative_path), ''))
            if test_file and (self.project_root / test_file).exists():
                subprocess.run(['python', '-m', 'unittest', str(test_file)])
            else:
                # o1-mini: If no specific test is found, run all tests
                subprocess.run(['python', '-m', 'unittest', 'discover', '-s', 'tests'])

if __name__ == "__main__":
    project_root = '.'  # o1-mini: Define the project root directory

    # o1-mini: Preload test mappings
    test_mapping = preload_test_mapping(Path(project_root), manual_test_mapping)

    event_handler = TestRunnerHandler(test_mapping, project_root)
    observer = Observer()
    observer.schedule(event_handler, path=project_root, recursive=True)
    observer.start()
    print('Watching for changes...')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()