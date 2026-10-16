# Lab 5: Static Code Analysis - Issues Found and Fixed

**File analysed:** `society_dues.py` (Apartment Society Maintenance Dues Ledger)

**Scores:** Pylint 5.81/10 before, 10.00/10 after. Bandit 3 issues before, 0 after. Flake8 5 issues before, 0 after.

Line numbers refer to the original file, as shown in the `*_before.txt` reports.

| Issue | Type | Line(s) | Description | Fix Approach |
| ----- | ---- | ------- | ----------- | ------------ |
| Use of `eval()` (Bandit B307 / Pylint W0123) | Security (Medium) | 21 | `penalty()` ran `eval(rule)`, which executes any text passed in as code. A malicious rule string could run arbitrary commands. | Removed `eval`. Parsed the rule with `ast.parse` and wrote a small `_safe_eval` that only allows numbers and `+ - * /`. Output stays the same (`50 * 2` gives `100`). |
| SQL injection (Bandit B608) | Security (Medium) | 9 | `addDue` built the INSERT query with an f-string, so `flat` or `month` could inject SQL. | Switched to a parameterised query: `INSERT INTO dues VALUES (?, ?, ?, 0)` with the values passed as a tuple. |
| Hardcoded password (Bandit B105) | Security (Low) | 5 | `TREASURER_PASSWORD = "flat#101"` keeps a secret in the source code and in Git history. | Read it from an environment variable with `os.environ.get("TREASURER_PASSWORD", "")`. |
| Mutable default argument (Pylint W0102) | Bug | 8 | `history=[]` is created once and shared across every call, so history leaked between calls. | Changed the default to `None` and create a new list inside the function when `history is None`. |
| Overly broad exception (Pylint W0718) | Bug / Bad practice | 22 | `except Exception` in `penalty()` hid every kind of error, including real bugs. | Catch only the specific errors that can happen: `ValueError, SyntaxError, TypeError, ZeroDivisionError`. |
| Inconsistent return statements (Pylint R1710) | Bug | 12 | `collect()` returned `row[0]` when a due existed but returned nothing otherwise. | Added an explicit `return None` at the end so every path returns a value. |
| Comparison to None with `!=` (Flake8 E711 / Pylint C0121) | Style | 29 | `if rows != None` should use identity comparison, because `None` is a singleton. | Changed to `if rows is not None`. |
| Function name not snake_case (Pylint C0103) | Style | 8 | `addDue` is camelCase, which breaks PEP 8 naming. | Renamed to `add_due` and updated both calls in `main()`. |
| Missing docstrings (Pylint C0114 / C0116) | Style / Maintainability | 1, 8, 12, 19, 27, 34 | The module and every function had no docstring. | Added a module docstring and a one-line docstring to each function. |
| Lines too long (Flake8 E501 / Pylint C0301) | Style | 4, 13, 15 | Lines were longer than 79 characters (up to 104). | Split long strings and `conn.execute(...)` calls across several lines. |
| Missing blank lines (Flake8 E302) | Style | 12 | A function definition had no blank lines before it; PEP 8 requires two. | Added two blank lines before the function. |
| Trailing whitespace (Flake8 W291) | Style | 25 (after edits) | A stray space at the end of a line, introduced while editing. | Removed the trailing space. |

## Verification

After each fix, `python society_dues.py` still printed `2500`, `100`, `['A-102']`, so behaviour was unchanged. The reports are saved in `pylint_before.txt`, `bandit_before.txt`, `flake8_before.txt` (before) and `pylint_after.txt`, `bandit_after.txt`, `flake8_after.txt` (after).
