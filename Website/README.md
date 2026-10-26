# DB Lab 2 – Login & To-Do Application

## 1. Team
| Name | ID | Did what |
|------|----|----------|
| _Your name_ | _ID_ | _e.g. back end, SQL, README_ |
| _Partner (delete if alone)_ | _ID_ | _e.g. front end, validation, testing_ |

## 2. Technology
- Back end: Python 3 + Flask (sessions), PyMySQL (plain SQL, `%s` parameters), bcrypt
- Front end: Jinja templates, plain HTML/CSS (responsive, dark-mode aware), vanilla JavaScript
- Database: MySQL, database `registration`

## 3. How to run
1. Install Python 3.10+ and MySQL 8.
2. `git clone <repo-url> && cd db-lab2-<names>`
3. `python -m venv venv && source venv/bin/activate` (Windows: `venv\Scripts\activate`)
4. `pip install -r requirements.txt`
5. Build the database: `mysql -u <user> -p < database/schema.sql`
6. `cp .env.example .env` and fill in `DB_USER`, `DB_PASSWORD`, `SECRET_KEY`.
7. `python app.py`
8. Open http://127.0.0.1:5000

## 4. Features
- R1 Register (name, email, password, confirm) → "Email Already Exists" on duplicate (MySQL error 1062) → auto login
- R2 Login with the same "Invalid email or password" for unknown e-mail / wrong password; Logout destroys the session
- R3 Private list: `/todos` redirects to login when not logged in; each user sees only their own to-dos, newest first
- R4–R7 Add, edit title, mark done/not done, delete (with "are you sure?")
- R8 Same validation rules and exact messages in the browser (`static/app.js`) and on the server (`app.py`); on a server error the page is shown again and the database is not touched
- R9 bcrypt hashes, only the given queries, always parameterised, `user_id` taken from the session
- R10 Consistent responsive UI (works at 360 px), error messages next to forms, done state, empty state, friendly error pages
- Bonus: dark mode (follows the system setting)

## 5. Screenshots
Put at least four in `screenshots/`: register with errors, login, list with to-dos (one done), phone-sized window.

## 6. Answers
**(a) Why `AND user_id = ?` in UPDATE and DELETE?** The to-do id comes from the browser, so anybody can send another user's id. With `AND user_id = ?` (taken from the session) the statement matches zero rows when the to-do is not yours. Without it, any logged-in user could edit or delete anybody's to-dos just by changing the number.

**(b) Inserting a to-do for a non-existent `user_id`?** MySQL rejects it with error 1452 (a foreign key constraint fails). This is the **referential integrity constraint** (foreign key): every `todos.user_id` must match an existing `users.user_id`.

**(c) Why store a hash, not the password?** If the database leaks, attackers get no usable passwords, and not even admins can read them. bcrypt is one-way, salted (equal passwords give different hashes) and deliberately slow, which makes guessing attacks expensive. MD5/SHA are fast and unsalted, so they are easy to crack.

**(d) Why check for an empty name when `name` is NOT NULL?** `NOT NULL` only forbids NULL. An empty text `''` (or spaces) is a value, so MySQL accepts it. Only our own checks (browser and server) can refuse it.
