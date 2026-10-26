from flask import Flask, render_template, request, redirect, session
import os
from decimal import Decimal, InvalidOperation
import pymysql
import bcrypt
from dotenv import load_dotenv
from flask_session import Session
from cachelib.file import FileSystemCache

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SESSION_TYPE"] = "cachelib"
app.config["SESSION_CACHELIB"] = FileSystemCache(".sessions")
app.config["SESSION_PERMANENT"] = False

Session(app)


# Connect to the original database or a specified database.
def get_connection(database=None):
    if database is None:
        database = os.getenv("DB_NAME")

    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route("/")
def home():
    return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def register():
    errors = []

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name:
            errors.append("Name is required")

        if not email:
            errors.append("Email is required")

        if not password:
            errors.append("Password is required")

        if not confirm_password:
            errors.append("Confirm password is required")

        if password and confirm_password and password != confirm_password:
            errors.append("Passwords do not match")

        if len(name) > 100:
            errors.append("Name is too long")

        if len(email) > 255:
            errors.append("Email is too long")

        if len(password.encode("utf-8")) > 72:
            errors.append("Password must be at most 72 bytes")

        if not errors:
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            connection = None

            try:
                connection = get_connection()

                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO users (email, name, password_hash) "
                        "VALUES (%s, %s, %s)",
                        (email, name, password_hash)
                    )

                    user_id = cursor.lastrowid

                connection.commit()

            except pymysql.IntegrityError as error:
                if error.args[0] == 1062:
                    errors.append("Email Already Exists")
                else:
                    errors.append("Could not create the account")

            except pymysql.MySQLError as error:
                print("MySQL error:", error)
                errors.append("Database unavailable. Please try again")

            finally:
                if connection is not None:
                    connection.close()

            if not errors:
                session.clear()
                session["user_id"] = user_id
                session["name"] = name
                app.session_interface.regenerate(session)

                return redirect("/todos")

    return render_template("register.html", errors=errors)


@app.route("/todos")
def todos():
    if "user_id" not in session:
        return redirect("/register")

    return render_template("todos.html")


# F2.1: Display authors and books using SELECT.
@app.route("/library")
def library():
    if "user_id" not in session:
        return redirect("/register")

    connection = get_connection("library")

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM AUTHOR")
            authors = cursor.fetchall()

            cursor.execute("SELECT * FROM BOOK")
            books = cursor.fetchall()

    finally:
        connection.close()

    return render_template(
        "library.html",
        authors=authors,
        books=books
    )


# F2.2: Add an author using INSERT.
@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if "user_id" not in session:
        return redirect("/register")

    errors = []

    if request.method == "POST":
        author_id_text = request.form.get("author_id", "").strip()
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()

        try:
            author_id = int(author_id_text)

            if not 1 <= author_id <= 2147483647:
                errors.append("Enter a valid positive author ID.")

        except ValueError:
            errors.append("Author ID must be a whole number.")

        if not name or len(name) > 100:
            errors.append("Enter a name of up to 100 characters.")

        if not country or len(country) > 50:
            errors.append("Enter a country of up to 50 characters.")

        if not errors:
            connection = None

            try:
                connection = get_connection("library")

                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO AUTHOR (author_id, name, country) "
                        "VALUES (%s, %s, %s)",
                        (author_id, name, country)
                    )

                connection.commit()
                return redirect("/library")

            except pymysql.IntegrityError as error:
                if connection is not None:
                    connection.rollback()

                if error.args[0] == 1062:
                    errors.append("This author ID already exists.")
                else:
                    errors.append("Could not add the author.")

            except pymysql.MySQLError as error:
                if connection is not None:
                    connection.rollback()

                print("MySQL error:", error)
                errors.append("Database unavailable. Please try again.")

            finally:
                if connection is not None:
                    connection.close()

    return render_template("add_author.html", errors=errors)


# F2.2: Add a book using INSERT.
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if "user_id" not in session:
        return redirect("/register")

    errors = []
    authors = []
    connection = None

    try:
        connection = get_connection("library")

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM AUTHOR")
            authors = cursor.fetchall()

        if request.method == "POST":
            book_id_text = request.form.get("book_id", "").strip()
            title = request.form.get("title", "").strip()
            price_text = request.form.get("price", "").strip()
            author_id_text = request.form.get("author_id", "").strip()

            try:
                book_id = int(book_id_text)

                if not 1 <= book_id <= 2147483647:
                    errors.append("Enter a valid positive book ID.")

            except ValueError:
                errors.append("Book ID must be a whole number.")

            if not title or len(title) > 150:
                errors.append("Enter a title of up to 150 characters.")

            try:
                price = Decimal(price_text)

                if not price.is_finite():
                    errors.append("Enter a valid price.")

                elif not 0 <= price <= Decimal("99999999.99"):
                    errors.append(
                        "Price must be between 0 and 99999999.99."
                    )

                elif price != price.quantize(Decimal("0.01")):
                    errors.append("Use at most two decimal places.")

            except InvalidOperation:
                errors.append("Enter a valid price.")

            valid_author_ids = [
                str(author["author_id"]) for author in authors
            ]

            if author_id_text not in valid_author_ids:
                errors.append("Choose an existing author.")

            if not errors:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO BOOK "
                        "(book_id, title, price, author_id) "
                        "VALUES (%s, %s, %s, %s)",
                        (
                            book_id,
                            title,
                            price,
                            int(author_id_text)
                        )
                    )

                connection.commit()
                return redirect("/library")

    except pymysql.IntegrityError as error:
        if connection is not None:
            connection.rollback()

        if error.args[0] == 1062:
            errors.append("This book ID already exists.")
        elif error.args[0] == 1452:
            errors.append("The selected author no longer exists.")
        else:
            errors.append("Could not add the book.")

    except pymysql.MySQLError as error:
        if connection is not None:
            connection.rollback()

        print("MySQL error:", error)
        errors.append("Database unavailable. Please try again.")

    finally:
        if connection is not None:
            connection.close()

    return render_template(
        "add_book.html",
        errors=errors,
        authors=authors
    )


# F2.3: Edit an author using UPDATE.
@app.route("/edit_author/<int:author_id>", methods=["GET", "POST"])
def edit_author(author_id):
    if "user_id" not in session:
        return redirect("/register")

    errors = []
    author = None
    connection = None

    try:
        connection = get_connection("library")

        with connection.cursor() as cursor:
            # Retrieve the selected author by primary key.
            cursor.execute(
                "SELECT * FROM AUTHOR WHERE author_id = %s",
                (author_id,)
            )
            author = cursor.fetchone()

        if author is None:
            return "Author not found", 404

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            country = request.form.get("country", "").strip()

            if not name or len(name) > 100:
                errors.append("Enter a name of up to 100 characters.")

            if not country or len(country) > 50:
                errors.append("Enter a country of up to 50 characters.")

            # Keep entered values visible if validation fails.
            author["name"] = name
            author["country"] = country

            if not errors:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE AUTHOR "
                        "SET name = %s, country = %s "
                        "WHERE author_id = %s",
                        (name, country, author_id)
                    )

                connection.commit()
                return redirect("/library")

    except pymysql.MySQLError as error:
        if connection is not None:
            connection.rollback()

        print("MySQL error:", error)

        if author is None:
            return "Database unavailable. Please try again.", 503

        errors.append("Could not save the changes. Please try again.")

    finally:
        if connection is not None:
            connection.close()

    return render_template(
        "edit_author.html",
        author=author,
        errors=errors
    )


# F2.3: Edit a book using UPDATE.
@app.route("/edit_book/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if "user_id" not in session:
        return redirect("/register")

    errors = []
    book = None
    authors = []
    connection = None

    try:
        connection = get_connection("library")

        with connection.cursor() as cursor:
            # Retrieve the selected book by primary key.
            cursor.execute(
                "SELECT * FROM BOOK WHERE book_id = %s",
                (book_id,)
            )
            book = cursor.fetchone()

            # Retrieve authors for the selection list.
            cursor.execute("SELECT * FROM AUTHOR")
            authors = cursor.fetchall()

        if book is None:
            return "Book not found", 404

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            price_text = request.form.get("price", "").strip()
            author_id_text = request.form.get("author_id", "").strip()

            if not title or len(title) > 150:
                errors.append("Enter a title of up to 150 characters.")

            try:
                price = Decimal(price_text)

                if not price.is_finite():
                    errors.append("Enter a valid price.")

                elif not 0 <= price <= Decimal("99999999.99"):
                    errors.append(
                        "Price must be between 0 and 99999999.99."
                    )

                elif price != price.quantize(Decimal("0.01")):
                    errors.append("Use at most two decimal places.")

            except InvalidOperation:
                errors.append("Enter a valid price.")

            valid_author_ids = [
                str(author["author_id"]) for author in authors
            ]

            if author_id_text not in valid_author_ids:
                errors.append("Choose an existing author.")

            # Keep entered values visible if validation fails.
            book["title"] = title
            book["price"] = price_text
            book["author_id"] = author_id_text

            if not errors:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE BOOK "
                        "SET title = %s, price = %s, author_id = %s "
                        "WHERE book_id = %s",
                        (
                            title,
                            price,
                            int(author_id_text),
                            book_id
                        )
                    )

                connection.commit()
                return redirect("/library")

    except pymysql.IntegrityError:
        if connection is not None:
            connection.rollback()

        errors.append("The selected author no longer exists.")

    except pymysql.MySQLError as error:
        if connection is not None:
            connection.rollback()

        print("MySQL error:", error)

        if book is None:
            return "Database unavailable. Please try again.", 503

        errors.append("Could not save the changes. Please try again.")

    finally:
        if connection is not None:
            connection.close()

    return render_template(
        "edit_book.html",
        book=book,
        authors=authors,
        errors=errors
    )


if __name__ == "__main__":
    app.run()