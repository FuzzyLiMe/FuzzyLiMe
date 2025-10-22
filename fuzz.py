import sys
import ollama
import os
import subprocess
from pathlib import Path
import shutil

# Usage: python fuzz.py [target] [format]
MODEL = 'llama3:latest'
TARGET = ''
FORMAT = ''


def resolve_executable(target: str) -> str | None:
    """Resolve a target name/path to an executable path.
    Returns absolute path string if found, or None.
    """
    script_dir = Path(__file__).parent

    # If empty target, nothing to do
    if not target:
        return None

    p = Path(target)

    # If target is absolute -> use it directly (but still try adding .exe on Windows)
    if p.is_absolute():
        candidate = p
    else:
        # Append the path parts to the script directory so "vulnerable/vuln"
        # becomes script_dir / 'vulnerable' / 'vuln'
        candidate = script_dir.joinpath(*p.parts)

    # If candidate exists and is a file, return it (use .resolve() for absolute)
    if candidate.exists() and candidate.is_file():
        return str(candidate.resolve())

    # On Windows: try adding .exe suffix to the candidate path
    if os.name == 'nt':
        maybe = candidate.with_suffix('.exe')
        if maybe.exists() and maybe.is_file():
            return str(maybe.resolve())

    # If not found by path, try locating on PATH (shutil.which)
    which = shutil.which(target)
    if which:
        return which

    # On Windows, try looking for target + .exe on PATH too
    if os.name == 'nt':
        which_exe = shutil.which(target + '.exe')
        if which_exe:
            return which_exe

    return None


def get_fuzz_cases(format_str: str) -> list[str]:

    message = {
        'role': 'user', 
        'content': f"Can you generate me a fuzzing test case for a C program with the following input format?\n{format_str}\nReturn the test case only without any other words."
    }

    output_str = ""
    try:
        for part in ollama.chat(model=MODEL, messages=[message], stream=True):
            output_str += part['message']['content']
    except Exception as e:
        print('\nError running ollama.chat:', e)
        print('If the model is installed but you still see errors, try running the model with the CLI:')
        print(f'  ollama run {MODEL}')
        sys.exit(1)

    return output_str.split(' ')


def main():
    global TARGET, FORMAT

    if len(sys.argv) < 2:
        print("Usage: python fuzz.py [target]")
        sys.exit(1)

    TARGET = resolve_executable(sys.argv[1])
    FORMAT = resolve_executable(sys.argv[2])

    with open(FORMAT, 'r') as file:
        format_str = file.read()

    cases = get_fuzz_cases(format_str)

    print('Fuzz cases generated:', cases)
    res = subprocess.run([TARGET] + cases, capture_output=True, text=True, timeout=10)
    print('exit', res.returncode)


if __name__ == '__main__':
  main()
