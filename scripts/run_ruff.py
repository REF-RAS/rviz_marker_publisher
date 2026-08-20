import subprocess
import sys
from pathlib import Path
import pytest

def format_and_lint_folders(folders_list: list[str]) -> None:
    """Auto-format line lengths and lint selected folders using Ruff."""
    print(f"Starting Ruff processing on: {', '.join(folders_list)}\n")
    errors_found = False

    for folder in folders_list:
        path = Path(folder)
        if not path.is_dir():
            print(f'❌ Error: Folder {folder} does not exist. Skipping.')
            continue

        print(f'🧹 1. Auto-formatting lines in: {folder}...')
        
        # 'ruff format' splits long expressions, wraps lines, and cleans layout
        format_command = [
            'ruff', 'format', str(path),
            '--line-length', '160'  # Sets max allowed line limit (Default is 88)
        ]
        subprocess.run(format_command, capture_output=True, text=True)

        print(f'🔍 2. Running lint checks on: {folder}...')
        
        # 'ruff check' fixes imports/styles while reporting unfixable problems
        check_command = [
            'ruff', 'check', str(path),
            '--select', 'E,W,F,D',
            '--line-length', '160',
            '--fix'  # Autofixes other fixable lint errors automatically
        ]
        result = subprocess.run(check_command, capture_output=True, text=True)

        if result.returncode == 0:
            print(f'✅ {folder}: Successfully formatted and passed linting.')
        else:
            print(f'⚠️ {folder}: Formatting applied, but manual fixes needed:')
            print(result.stdout)
            errors_found = True

    if errors_found:
        sys.exit(1)

def test():
    print('test')
    target_folders = ['rviz_marker_publisher']
    format_and_lint_folders(target_folders)

if __name__ == '__main__':
    test()