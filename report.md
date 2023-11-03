# Project Setup and Execution Guide

Follow these steps to set up the project environment and run the code:

### Step 1: Check Python and Pip Version
Ensure you have the correct versions of Python and pip installed:
```bash
python --version
pip --version
```

### Step 2: Create a Virtual Environment
Create an isolated environment for your Python project:
```bash
virtualenv venv
```

### Step 3: Activate Virtual Environment
Activate the virtual environment. On Unix or MacOS, use:
```bash
source venv/bin/activate
```


### Step 4: Install Necessary Packages
Install all the necessary packages from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### Step 5: Verify Python Interpreter in Virtual Environment
Check that the Python interpreter is now set to the virtual environment's interpreter:
```bash
which python
```

### Step 6: Run the Code
Execute the main script to run the project:
```bash
python pipeline.py
```

### Step 7: Check the Results

You can check generated PNG files in results folder
Or check the db.
```bash
sqlite3 sales_database.db
```
List tables using
```bash
.tables
```
Query the contents of a table
```bash
SELECT * FROM table_name;
```