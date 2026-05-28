# Imported os for file system access, boto3 for AWS S3 operations, and botocore for catching AWS-specific errors
import os
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# DATA_FILE is the local text file where student records are stored between sessions
# S3_BUCKET is the name of your S3 bucket — change this to match your actual bucket name
DATA_FILE = "students.txt"
S3_BUCKET = "test-bucket-48156161"   # replace with your bucket name. Bucket must already exist.
S3_KEY = "students.txt"             # the object key (path) inside the bucket


# load_students() checks if the local file exists, then reads each comma-separated line
# and converts it back into a list of student dictionaries
def load_students():
    students = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    name = parts[0]
                    grade = float(parts[1])
                    passed = parts[2] == "True"
                    students.append({"name": name, "grade": grade, "passed": passed})
    return students


# save_students() writes each student as a single comma-separated line to the local file
# format: Name,Grade,PassedStatus  (e.g. "Alice,88.0,True")
def save_students(students):
    with open(DATA_FILE, "w") as f:
        for s in students:
            f.write(f"{s['name']},{s['grade']},{s['passed']}\n")
    print(f"  Saved {len(students)} student(s) to {DATA_FILE}.\n")


# add_student() prompts the user for a name and a numeric grade (0-100),
# validates both inputs, then appends the new record to the in-memory list
def add_student(students):
    name = input("Enter student name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return

    while True:
        try:
            grade = float(input(f"Enter {name}'s grade (0-100): "))
            if 0 <= grade <= 100:
                break
            print("Grade must be between 0 and 100.")
        except ValueError:
            print("Please enter a valid number.")

    # A grade of 60 or above counts as passing
    students.append({"name": name, "grade": grade, "passed": grade >= 60})
    print(f"  {name} added.\n")


# view_students() prints a formatted table of every student with their grade and pass/fail status,
# then shows the class average and how many students are passing
def view_students(students):
    if not students:
        print("No students on record.\n")
        return

    print("\n=== Student Report ===")
    print(f"{'Name':<20} {'Grade':>6}  {'Status'}")
    print("-" * 38)

    for s in students:
        status = "PASS" if s["passed"] else "FAIL"
        print(f"{s['name']:<20} {s['grade']:>6.1f}  {status}")

    average = sum(s["grade"] for s in students) / len(students)
    passing = sum(1 for s in students if s["passed"])
    print(f"\nClass average   : {average:.1f}")
    print(f"Students passing: {passing}/{len(students)}\n")


# upload_to_s3() saves the current student list to the local file first,
# then uses boto3 to upload that file to the configured S3 bucket
def upload_to_s3(students):
    # Save locally before uploading so the file is always up to date
    save_students(students)

    try:
        # boto3 automatically uses credentials from ~/.aws/credentials or environment variables
        s3 = boto3.client("s3")
        s3.upload_file(DATA_FILE, S3_BUCKET, S3_KEY)
        print(f"  Uploaded {DATA_FILE} to s3://{S3_BUCKET}/{S3_KEY}\n")
    except ClientError as e:
        # ClientError covers things like missing bucket, wrong permissions, or invalid key
        print(f"  Upload failed: {e}\n")
    except BotoCoreError as e:
        # BotoCoreError covers lower-level issues like no network or bad credentials
        print(f"  AWS connection error: {e}\n")


# download_from_s3() fetches the student file from S3 and overwrites the local copy,
# then reloads and returns the refreshed list so the menu keeps working with fresh data
def download_from_s3():
    try:
        s3 = boto3.client("s3")
        # download_file saves the S3 object directly to the local DATA_FILE path
        s3.download_file(S3_BUCKET, S3_KEY, DATA_FILE)
        print(f"  Downloaded s3://{S3_BUCKET}/{S3_KEY} to {DATA_FILE}")

        # Reload the student list from the newly downloaded file
        students = load_students()
        print(f"  Refreshed — {len(students)} student(s) loaded.\n")
        return students
    except ClientError as e:
        print(f"  Download failed: {e}\n")
    except BotoCoreError as e:
        print(f"  AWS connection error: {e}\n")

    # Return an empty list if the download failed so the program can continue safely
    return []


# main() is the program entry point — it loads any existing local data, then loops
# through a menu that lets the user add, view, save, upload, download, or exit
def main():
    # Try to load existing records from the local file on startup
    students = load_students()
    print("=== Student Records System ===")
    print(f"Loaded {len(students)} student(s) from local file.\n")

    while True:
        print("1. Add student")
        print("2. View all students")
        print("3. Save to local file")
        print("4. Upload to S3")
        print("5. Download from S3 (refresh local data)")
        print("6. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_student(students)

        elif choice == "2":
            view_students(students)

        elif choice == "3":
            # Saves the current in-memory list to the local text file
            save_students(students)

        elif choice == "4":
            # Saves locally and then pushes the file up to S3
            upload_to_s3(students)

        elif choice == "5":
            # Pulls the latest file from S3 and replaces the in-memory list
            students = download_from_s3()

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please enter 1-6.\n")


main()
