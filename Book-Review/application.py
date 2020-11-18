import os
import requests

from flask import Flask, session, render_template, redirect, request, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    ''' Homepage '''

    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    ''' Register the user '''

    # Forget any users
    session.clear()

    # User reached route via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message = "Must provide username.", code = 403)

        # Check if the username already exists
        row = db.execute("SELECT * FROM users WHERE username = :username",
                        {"username": request.form.get("username")}).fetchone()

        # If exists, return error
        if row:
            return render_template("error.html", message = "Username taken.", code = 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message = "Must provide password.", code = 403)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return render_template("error.html", message = "Must confirm password.", code = 403)

        # Ensure password and confirmation are the same
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", message = "Password and confirmation are not the same", code = 403)

        # Hash password
        hashPassword = generate_password_hash(request.form.get("password"))

        # Append user to the db
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                            {"username": request.form.get("username"),
                             "hash": hashPassword})

        # Commit changes to db
        db.commit()

        # Confirmation message
        flash("Registered!")

        # Remember the user
        user = db.execute("SELECT * FROM users WHERE username = :username",
                        {"username": request.form.get("username")}).fetchone()
        session["user_id"] = user[0]

        # Redirect to dashboard
        return redirect("/dashboard")

    # User reached route via GET
    else:    
        return render_template("register.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    ''' Log user in '''

    # Forget any users
    session.clear()

    # User reached route via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message = "Must provide username.", code = 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message = "Must provide password.", code = 403)

        # See if the user exists in db
        result = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": request.form.get("username")}).fetchone()

        # Ensure username exists and pwd is correct
        if result == None or not check_password_hash(result[2], request.form.get("password")):
            return render_template("error.html", message = "Username or password incorrect.", code = 403)

        # Remember which user logged in
        session["user_id"] = result[0]

        # Redirect to dashboard
        return redirect("/dashboard")

    # User reached route via GET
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    ''' Log user out '''

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/dashboard", methods = ["GET", "POST"])
@login_required
def dashboard():
    ''' Search for books '''
    
    # User via POST
    if request.method == "POST":

        # Check if there is any input
        if not request.form.get("book"):
            return render_template("error.html", message = "Please provide ISBN / Title / Author", code = 403)

        # If user typed only part of input
        q = "%" + request.form.get("book") + "%"

        # format input in title case
        q = q.title()

        # Query db for input
        result = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                            isbn LIKE :q OR \
                            title LIKE :q OR \
                            author LIKE :q",
                            {"q": q}).fetchall()

        # Return error if no books found
        if len(result) == 0:
            return render_template("error.html", message = "No books found", code = 404)

        # Display all results
        return render_template("result.html", result=result)

    # User via GET
    else:
        return render_template("dashboard.html")

@app.route("/book/<isbn>", methods = ["GET", "POST"])
def book(isbn):
    ''' Display book page for each isbn '''

    # If user via POST
    if request.method == "POST":

        # Save current user info
        currentUser = session["user_id"]
        
        # Fetch form data
        rating = request.form.get("rating")
        comment = request.form.get("comment")
        
        # Search book_id by ISBN
        row = db.execute("SELECT books_id FROM books WHERE isbn = :isbn",
                            {"isbn": isbn})
        
        # Save the book id
        bookId = row.fetchone() # Returns a tuple
        bookId = bookId[0]

        # Check if user already reviewed
        result = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                            {"user_id": session["user_id"],
                            "book_id": bookId})

        userReview = result.first()

        # A review already exists
        if userReview:
            
            # Display error message
            return render_template("error.html", message = "Review already submitted.", code = 422)

        # Convert rating to save into DB
        rating = int(rating)

        db.execute("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES (:user_id, :book_id, :comment, :rating)",
                    {"user_id": currentUser, 
                    "book_id": bookId,
                    "comment": comment, 
                    "rating": rating})

        db.commit()

        flash("Successful")

        # Return user to the same page
        return redirect("/book/" + isbn)
    
    # User via GET
    else:
        bookInfo = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn",
                            {"isbn": isbn}).fetchall()

        # Call GoodReads API for info
        # Read API key from env variable
        key = os.getenv("GOODREADS_KEY")
        
        # Query the api with key and ISBN as parameters
        q = requests.get("https://www.goodreads.com/book/review_counts.json",
                        params={"key": key, "isbns": isbn})

        # Convert the response to JSON
        response = q.json()

        # "Clean" the JSON before passing it to the bookInfo list
        response = response['books'][0]

        # Append it as the second element on the list
        bookInfo.append(response)

        # User review
        # Search book_id by ISBN
        row = db.execute("SELECT books_id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn}).fetchone()

        book = row[0]

        # Fetch book reviews
        reviews = db.execute("SELECT comment, rating \
                            FROM reviews \
                            WHERE book_id = :book",
                            {"book": book}).fetchall()

        # Redirect user to the book page
        return render_template("book.html", bookInfo=bookInfo, reviews=reviews)


@app.route("/api/<isbn>", methods = ["GET"])
@login_required
def apiCall(isbn):
    ''' API '''

    # Query db for API info
    result = db.execute("SELECT title, author, year, isbn, \
                        COUNT(reviews.id) AS review_count, \
                        AVG(reviews.rating) AS average_score \
                        FROM books \
                        INNER JOIN reviews \
                        ON books.books_id = reviews.book_id \
                        WHERE isbn = :isbn \
                        GROUP BY title, author, year, isbn",
                        {"isbn": isbn}).fetchone()
    
    # If there is no return
    if result == None:
        return jsonify({"Error": "ISBN invalid"}), 422

    # Convert result list into a dict
    result = dict(result.items())

    # Convert average_score to a 2 point decimal
    # https://floating-point-gui.de/languages/python/
    result['average_score'] = float('%.2f'%(result['average_score']))

    # Return the JSON
    return jsonify(result)