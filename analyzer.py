import subprocess
import tempfile
import os
import re
import ast
from radon.complexity import cc_visit

def analyze_code(code):
    import subprocess
    import tempfile
    import os
    import re

    file_path = None

    try:
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as file:
            file.write(code)
            file_path = file.name

        # Analyze the code using Pylint
        result = subprocess.run(
            [
                "pylint",
                "--score=y",
                "--reports=n",
                file_path
            ],
            capture_output=True,
            text=True,
            timeout=15
        )

        output = result.stdout + "\n" + result.stderr

        # Extract the Pylint score
        match = re.search(
            r"rated at (-?\d+(?:\.\d+)?)/10",
            output
        )

        score = float(match.group(1)) if match else 0.0

        # Categorize detected issues
        issues = []
        errors = []
        warnings = []
        conventions = []

        for line in output.splitlines():
            if re.search(r": [A-Z]\d{4}:", line):
                issue = line.strip()
                issues.append(issue)

                if re.search(r": E\d{4}:", line):
                    errors.append(issue)

                elif re.search(r": W\d{4}:", line):
                    warnings.append(issue)

                elif re.search(r": [CR]\d{4}:", line):
                    conventions.append(issue)

        return {
            "score": score,
            "issues": issues,
            "errors": errors,
            "warnings": warnings,
            "conventions": conventions,
            "output": output
        }

    except subprocess.TimeoutExpired:
        return {
            "score": 0.0,
            "issues": ["Analysis timed out. Try a smaller file."],
            "errors": [],
            "warnings": [],
            "conventions": [],
            "output": "Analysis timed out."
        }

    except Exception as error:
        return {
            "score": 0.0,
            "issues": [str(error)],
            "errors": [],
            "warnings": [],
            "conventions": [],
            "output": str(error)
        }

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

def analyze_complexity(code):
    try:
        # Check whether the submitted code has valid Python syntax
        tree = ast.parse(code)

        # Analyze cyclomatic complexity
        blocks = cc_visit(code)

        results = []

        for block in blocks:
            results.append({
                "name": block.name,
                "complexity": block.complexity,
                "line": block.lineno
            })

        return results

    except SyntaxError as error:
        return {
            "error": f"Syntax error on line {error.lineno}: {error.msg}"
        }