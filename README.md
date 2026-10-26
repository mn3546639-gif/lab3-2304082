# Database Lab 3

Name: Mohamed Nader El-ashry  
Student ID: 2304082

## About

Part 1 creates the COMPANY database and tests foreign keys.

Part 2 is a library website where users can display, add, edit
and delete authors and books.

## Tools

Python, Flask, PyMySQL, MySQL, HTML and VS Code.

## How to run

1. Open MySQL Workbench and run these scripts in order:
   - problem1_DDL.sql
   - problem1_DML.sql
   - problem2_DDL.sql
   - problem2_DML.sql

   The DDL scripts delete and recreate their databases.
   Run each DML script once after its DDL script.

2. For a fresh installation, run website/database/schema.sql
   to create the Lab 2 registration tables.
   This script may delete existing registration data.

3. Open a terminal inside the website folder and run:

```bat
py -m venv .venv
.venv\Scripts\python.exe -m pip install Flask "PyMySQL[rsa]" bcrypt python-dotenv Flask-Session cachelib
```

4. Create a .env file beside app.py with your settings:

```env
SECRET_KEY=your_long_random_secret
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=registration
```

5. Start the website:

```bat
.venv\Scripts\python.exe app.py
```

6. Open http://127.0.0.1:5000/register and register.
   Then open http://127.0.0.1:5000/library.

## Website features

- Display authors and books.
- Add and edit authors and books.
- Delete a book.
- Delete an author and automatically delete their books.

The website uses SELECT, INSERT, UPDATE and DELETE.
Primary keys prevent duplicate IDs.
Foreign keys link books to existing authors.

## Notes

Problem 1 answers are in problem1_Answers.txt.
Keep the seed data for the discussion.
Do not upload .env, .venv or .sessions to GitHub.