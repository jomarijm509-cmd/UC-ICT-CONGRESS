# UC ICT Congress Registration System

Python + SQLite + Flask implementation of the Capstone Project 1 skills test
(University of Cebu, College of Computer Studies).

## Modules

- **Registration** — add, edit, delete student registrations
- **Attendance** — check in a student by ID number, with the three required prompts
  (not registered / successfully recorded / already exists)
- **Raffle** — filter by campus, reveal a random winner among attendees
- **Report (By Campus)** — filter by campus, generate a report with totals
- **Report (Summary)** — totals for every campus in one table

## Database

SQLite file `registration.db`, single `Registration` table matching the
data dictionary from the instructions:

| Column     | Type | Description              |
|------------|------|---------------------------|
| idNum      | text (PK) | Student's ID Number  |
| campus     | text | Student's Campus Name     |
| studFName  | text | Student's First Name      |
| studLName  | text | Student's Last Name       |
| amountPaid | number | Amount Paid              |
| attended   | text | "Yes" or "No"             |

## How to run this in VS Code

1. **Install VS Code extensions**: "Python" (by Microsoft) — optional but recommended.
2. **Open this folder** in VS Code: `File > Open Folder...` → select `uc-ict-congress`.
3. **Open a terminal** in VS Code: `Terminal > New Terminal`.
4. **(Recommended) Create a virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
6. **Initialize the database** (creates `registration.db` with sample data,
   safe to skip since `app.py` does this automatically on first run):
   ```bash
   python database.py
   ```
7. **Run the app:**
   ```bash
   python app.py
   ```
8. Open your browser to **http://127.0.0.1:5000**

## Resetting the sample data

Delete `registration.db` and run `python database.py` again to get a fresh
database seeded with the sample rows from the skills-test mockups.

## Project structure

```
uc-ict-congress/
├── app.py                  # Flask routes (all 5 modules)
├── database.py              # SQLite schema + seed data
├── requirements.txt
├── registration.db          # created automatically
├── static/
│   └── style.css
└── templates/
    ├── base.html
    ├── index.html            # Menu
    ├── registration.html
    ├── student_form.html     # Add/Edit
    ├── attendance.html
    ├── raffle.html
    ├── report_campus.html
    └── report_summary.html
```
