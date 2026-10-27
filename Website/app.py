import os
from decimal import Decimal, InvalidOperation
from functools import wraps

import bcrypt
import pymysql
from dotenv import load_dotenv
from flask import (Flask, abort, redirect, render_template, request, session, url_for)

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


def run(sql, args=(), fetch="none", db=None):
    """Run ONE parameterised statement. fetch: none | one | all."""
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=db or os.getenv("DB_NAME", "registration"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            if fetch == "one":
                return cur.fetchone()
            if fetch == "all":
                return cur.fetchall()
            return cur.rowcount
    finally:
        conn.close()


def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*a, **kw)
    return wrapped


def check_title(title):
    title = (title or "").strip()
    if not title:
        return title, ["Title is required"]
    if len(title) > 200:
        return title, ["Title is too long (200 characters at most)"]
    return title, []


# ---------- auth ----------
@app.route("/")
def index():
    return redirect(url_for("todos" if "user_id" in session else "login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("todos"))
    errors, form = [], {}
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        pw = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        form = {"name": name, "email": email}
        if not name:
            errors.append("Name is required")
        if not email:
            errors.append("Email is required")
        if not pw:
            errors.append("Password is required")
        if not confirm:
            errors.append("Confirm password is required")
        if pw and confirm and pw != confirm:
            errors.append("Passwords do not match")
        if not errors:
            pw_hash = bcrypt.hashpw(pw.encode()[:72], bcrypt.gensalt(12)).decode()
            try:
                run("INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
                    (email[:255], name[:100], pw_hash))
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1062:
                    errors.append("Email Already Exists")
                else:
                    raise
            else:
                user = run("SELECT user_id, name, password_hash FROM users WHERE email = %s",
                           (email[:255],), "one")
                session.clear()
                session["user_id"], session["name"] = user["user_id"], user["name"]
                return redirect(url_for("todos"))
    return render_template("register.html", errors=errors, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("todos"))
    errors, email = [], ""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        pw = request.form.get("password", "")
        if not email:
            errors.append("Email is required")
        if not pw:
            errors.append("Password is required")
        if not errors:
            user = run("SELECT user_id, name, password_hash FROM users WHERE email = %s",
                       (email,), "one")
            if user:
                stored_hash = user["password_hash"]
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode("utf-8")
                if bcrypt.checkpw(pw.encode("utf-8"), stored_hash):
                    session.clear()
                    session["user_id"], session["name"] = user["user_id"], user["name"]
                    return redirect(url_for("todos"))
                else:
                    errors.append("Invalid email or password")
            else:
                errors.append("Invalid email or password")
    return render_template("login.html", errors=errors, email=email)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- to-dos ----------
def show_list(errors=None, form_title="", edit_id=None, edit_title=""):
    rows = run("SELECT todo_id, title, is_done, created_at FROM todos "
               "WHERE user_id = %s ORDER BY todo_id DESC", (session["user_id"],), "all")
    return render_template("todos.html", todos=rows, errors=errors or [],
                           form_title=form_title, edit_id=edit_id, edit_title=edit_title)


@app.route("/todos")
@login_required
def todos():
    return show_list()


@app.route("/todos/add", methods=["POST"])
@login_required
def add():
    title, errors = check_title(request.form.get("title"))
    if errors:
        return show_list(errors, form_title=request.form.get("title", ""))
    run("INSERT INTO todos (user_id, title) VALUES (%s, %s)", (session["user_id"], title))
    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
@login_required
def edit(todo_id):
    title, errors = check_title(request.form.get("title"))
    if errors:
        return show_list(errors, edit_id=todo_id, edit_title=request.form.get("title", ""))
    run("UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s",
        (title, todo_id, session["user_id"]))
    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/done", methods=["POST"])
@login_required
def done(todo_id):
    is_done = 1 if request.form.get("is_done") == "1" else 0
    run("UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s",
        (is_done, todo_id, session["user_id"]))
    return redirect(url_for("todos"))


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
@login_required
def delete(todo_id):
    run("DELETE FROM todos WHERE todo_id = %s AND user_id = %s", (todo_id, session["user_id"]))
    return redirect(url_for("todos"))


# ---------- library ----------
def lib(sql, args=(), fetch="none"):
    return run(sql, args, fetch, db="library")


def show_library(errors=None, form=None):
    books = lib("SELECT book_id, title, price, author_id FROM BOOK ORDER BY book_id", fetch="all")
    authors = lib("SELECT author_id, name, country FROM AUTHOR ORDER BY author_id", fetch="all")
    return render_template("library.html", books=books, authors=authors,
                           errors=errors or [], form=form or {})


def check_author(form):
    name = form.get("name", "").strip()
    country = form.get("country", "").strip()
    errors = []
    if not name:
        errors.append("Author name is required")
    elif len(name) > 50:
        errors.append("Author name is too long (50 characters at most)")
    if len(country) > 50:
        errors.append("Country is too long (50 characters at most)")
    return name, country, errors


def check_book(form):
    title = form.get("title", "").strip()
    price_raw = form.get("price", "").strip()
    author_raw = form.get("author_id", "").strip()
    errors, price, author_id = [], None, None
    if not title:
        errors.append("Book title is required")
    elif len(title) > 100:
        errors.append("Book title is too long (100 characters at most)")
    try:
        price = Decimal(price_raw)
        if not price.is_finite() or price < 0 or price >= 10**8:
            errors.append("Price must be between 0 and 99999999.99")
    except InvalidOperation:
        errors.append("Price must be a number")
    try:
        author_id = int(author_raw)
    except ValueError:
        errors.append("Author id must be a whole number")
    return title, price, author_id, errors


@app.route("/library")
@login_required
def library():                                   # F2.1
    return show_library()


@app.route("/library/authors/add", methods=["POST"])
@login_required
def add_author():                                # F2.2
    name, country, errors = check_author(request.form)
    if errors:
        return show_library(errors, request.form)
    lib("INSERT INTO AUTHOR (name, country) VALUES (%s, %s)", (name, country or None))
    return redirect(url_for("library"))


@app.route("/library/books/add", methods=["POST"])
@login_required
def add_book():                                  # F2.2
    title, price, author_id, errors = check_book(request.form)
    if not errors:
        try:
            lib("INSERT INTO BOOK (title, price, author_id) VALUES (%s, %s, %s)",
                (title, price, author_id))
            return redirect(url_for("library"))
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1452:
                errors.append("This author id does not exist")
            else:
                raise
    return show_library(errors, request.form)


@app.route("/library/authors/<int:author_id>/edit", methods=["GET", "POST"])
@login_required
def edit_author(author_id):                      # F2.3
    author = lib("SELECT author_id, name, country FROM AUTHOR WHERE author_id = %s",
                 (author_id,), "one")
    if not author:
        abort(404)
    errors = []
    if request.method == "POST":
        name, country, errors = check_author(request.form)
        if not errors:
            lib("UPDATE AUTHOR SET name = %s, country = %s WHERE author_id = %s",
                (name, country or None, author_id))
            return redirect(url_for("library"))
        author = {"author_id": author_id, "name": request.form.get("name", ""),
                  "country": request.form.get("country", "")}
    return render_template("edit_author.html", author=author, errors=errors)


@app.route("/library/books/<int:book_id>/edit", methods=["GET", "POST"])
@login_required
def edit_book(book_id):                          # F2.3
    book = lib("SELECT book_id, title, price, author_id FROM BOOK WHERE book_id = %s",
               (book_id,), "one")
    if not book:
        abort(404)
    errors = []
    if request.method == "POST":
        title, price, author_id, errors = check_book(request.form)
        if not errors:
            try:
                lib("UPDATE BOOK SET title = %s, price = %s, author_id = %s WHERE book_id = %s",
                    (title, price, author_id, book_id))
                return redirect(url_for("library"))
            except pymysql.err.IntegrityError as e:
                if e.args[0] == 1452:
                    errors.append("This author id does not exist")
                else:
                    raise
        book = {"book_id": book_id, "title": request.form.get("title", ""),
                "price": request.form.get("price", ""),
                "author_id": request.form.get("author_id", "")}
    return render_template("edit_book.html", book=book, errors=errors)


@app.route("/library/books/<int:book_id>/delete", methods=["POST"])
@login_required
def delete_book(book_id):                        # F2.4
    lib("DELETE FROM BOOK WHERE book_id = %s", (book_id,))
    return redirect(url_for("library"))


@app.route("/library/authors/<int:author_id>/delete", methods=["POST"])
@login_required
def delete_author(author_id):                    # F2.5 (books deleted by ON DELETE CASCADE)
    lib("DELETE FROM AUTHOR WHERE author_id = %s", (author_id,))
    return redirect(url_for("library"))


# ---------- friendly errors ----------
@app.errorhandler(404)
def not_found(_):
    return render_template("error.html", msg="Page not found."), 404


@app.errorhandler(Exception)
def oops(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return render_template("error.html", msg=e.description), e.code
    app.logger.exception(e)
    return render_template("error.html", msg="Something went wrong. Please try again."), 500


if __name__ == "__main__":
    app.run(debug=False)