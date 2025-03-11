# Python Documentation Standards

This document defines the required documentation format for all Python code in the project, ensuring consistency, readability, and maintainability.

---

## **1️⃣ Module Headers**
Every Python file must start with a **module-level docstring** that includes the filename, version, and a brief description of its purpose.

### ✅ **Example**
```python
"""
watcher.py - Champion Select Watcher
Version: 0.1.0
Description:
    Monitors champion selection, evaluates team compositions.
"""
```

---

## **2️⃣ Function & Method Docstrings (Google Style)**
Every function and method must include a docstring explaining its purpose, expected inputs, outputs, and exceptions.

### ✅ **Function Docstring Example**
```python
def get_champion_data(champion_id: int) -> dict:
    """
    Fetches champion data based on champion ID.

    Args:
        champion_id (int): The ID of the champion to retrieve.

    Returns:
        dict: A dictionary containing champion stats, roles, and abilities.

    Raises:
        ValueError: If champion_id is invalid.
    """
    if champion_id <= 0:
        raise ValueError("Invalid champion ID.")
    
    return {"id": champion_id, "name": "ExampleChamp"}
```

### ✅ **Class Docstring Example**
```python
class Watcher:
    """
    Class for monitoring ARAM champion selection.

    Attributes:
        champions (list): List of champions in the current match.
    """

    def __init__(self):
        """
        Initializes the Watcher instance.
        """
        self.champions = []

    def start(self):
        """
        Starts monitoring the ARAM champion selection.
        """
        print("Watching champion select...")
```

---

## **3️⃣ Private Methods & One-Liners**
For **simple functions**, use a one-line docstring.

### ✅ **One-Liner Function**
```python
def get_version() -> str:
    """Returns the current version of the application."""
    return "0.1.0"
```

For **private methods (`_method()`)**, document them like normal functions.

### ✅ **Private Method Example**
```python
def _sanitize_input(data: str) -> str:
    """
    Cleans input data before processing.
    """
    return data.strip()
```

---

## **4️⃣ In-Line Comments**
- Use in-line comments **only when necessary** to clarify complex logic.
- Do **not** state obvious information.

### ✅ **Good Example**
```python
# Fetch data from API and sanitize it
champ_data = fetch_champion_data(champ_id)
```

### ❌ **Bad Example**
```python
x = 10  # Set x to 10
```

---

## **5️⃣ Enforcing These Standards**

To ensure compliance, use automated tools:
1. **`pydocstyle`** – Checks if docstrings follow Google Style.
   ```bash
   pip install pydocstyle
   pydocstyle watcher.py
   ```
2. **`pre-commit hooks`** – Enforce documentation in commits.
   ```yaml
   repos:
     - repo: https://github.com/PyCQA/pydocstyle
       rev: "2.1.1"
       hooks:
         - id: pydocstyle
   ```
3. **Code Reviews** – PRs must include docstrings for new functions/classes.

---

## **6️⃣ Summary: Documentation Rules**
| **Requirement** | **Standard** |
|---------------|-------------|
| **Module Headers** | `"""module.py - Description"""` |
| **Function Docstrings** | Google Style (`Args:`, `Returns:`, `Raises:`) |
| **Class Docstrings** | Include `Attributes:` & method docstrings |
| **One-Liners** | `"""Simple function description."""` |
| **In-Line Comments** | Use **only when necessary** |
| **Automation** | `pydocstyle` + pre-commit hooks |

This document ensures all Python code in the project remains clear, maintainable, and well-documented. 🚀
