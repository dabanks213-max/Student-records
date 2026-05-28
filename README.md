# Student Grade Tracker with AWS S3 Integration

## Overview

This project is a Python-based Student Grade Tracker application that allows users to add, view, and store student records. The application stores data locally in a text file (`students.txt`) and can upload or download that file to/from Amazon S3 using Boto3.

The program demonstrates core programming concepts including lists, dictionaries, file input/output, and cloud integration with AWS.

---

## Features

- Add new student records (name and grade)
- View all student records in a formatted report
- Automatically determine pass/fail status (60 or above = pass)
- Display class average and number of passing students
- Save student data to a local text file
- Upload the data file to Amazon S3
- Download the data file from S3 to refresh local records

---

## Technologies Used

- Python 3
- [Amazon Boto3](https://pypi.org/project/boto3/) — AWS SDK for Python
- Amazon S3 — cloud storage
- Text file storage (`students.txt`)

---

## How to Run the Program

1. **Install Python 3** — [python.org](https://www.python.org/downloads/)

2. **Install Boto3:**
   ```bash
   pip install boto3
   ```

3. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

4. **Update the bucket name in `student_records.py`:**
   ```python
   S3_BUCKET = "your-bucket-name"
   ```
   > The bucket must already exist in your AWS account.

5. **Run the program:**
   ```bash
   python student_records.py
   ```

---

## Code Walkthrough

### Loading Students from File

```python
def load_students():
    students = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    students.append({"name": parts[0], "grade": float(parts[1]), "passed": parts[2] == "True"})
    return students
```

Reads `students.txt` on startup and converts each line into a student dictionary.

### Adding a Student

```python
students.append({"name": name, "grade": grade, "passed": grade >= 60})
```

Each student is stored as a dictionary and added to the in-memory list. A grade of 60 or above sets `passed` to `True`.

### Saving to a File

```python
def save_students(students):
    with open(DATA_FILE, "w") as f:
        for s in students:
            f.write(f"{s['name']},{s['grade']},{s['passed']}\n")
```

Writes all student records to `students.txt` in comma-separated format.

### Uploading to S3

```python
s3 = boto3.client("s3")
s3.upload_file(DATA_FILE, S3_BUCKET, S3_KEY)
```

Saves locally first, then uploads the file to the configured S3 bucket.

### Downloading from S3

```python
s3.download_file(S3_BUCKET, S3_KEY, DATA_FILE)
students = load_students()
```

Fetches the latest file from S3, overwrites the local copy, and reloads the student list.

---

## Sample Program Output

```
=== Student Records System ===
Loaded 2 student(s) from local file.

1. Add student
2. View all students
3. Save to local file
4. Upload to S3
5. Download from S3 (refresh local data)
6. Exit
Choose an option: 2

=== Student Report ===
Name                  Grade  Status
--------------------------------------
Alice                  88.0  PASS
Bob                    55.0  FAIL

Class average   : 71.5
Students passing: 1/2
```

---

## Example Data File

`students.txt` stores records in the following format:

```
Alice,88.0,True
Bob,55.0,False
Charlie,73.5,True
```

Fields: `Name`, `Grade`, `Passed`

---

## Challenges Faced

One challenge was handling AWS authentication errors when uploading files. Using `try/except` blocks for both `ClientError` and `BotoCoreError` allows the program to report specific issues (e.g., missing bucket, bad credentials, no network) without crashing.

Another challenge was keeping in-memory data in sync with the local file and S3. This was solved by always saving locally before uploading, and reloading from file immediately after downloading.

---

## What I Learned

Through this project, I learned how to:

- Use lists and dictionaries together to model real data
- Read and write files in Python for persistent storage
- Use Boto3 to interact with AWS S3
- Upload and download files from the cloud
- Build a menu-driven command-line application
- Handle errors gracefully with `try/except`

---

## Future Improvements

- Add a graphical user interface (GUI)
- Store data in JSON format instead of plain text
- Add student search and delete functionality
- Prevent duplicate student entries
- Add grade editing support
- Deploy as a web application with a REST API

---
