from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    username = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = :id", id=username)[0]
    username = user["username"]

    # Use SQL query to calculate portfolio
    portfolio = db.execute("""
        SELECT symbol, SUM(shares) as total_shares, price, SUM(total_price) as total_price
        FROM purchases
        WHERE username = :username
        GROUP BY symbol
        HAVING total_shares > 0
    """, username=username)

    cash = user["cash"]
    total = cash

    for stock in portfolio:
        total += stock["total_price"]

    return render_template("index.html", portfolio=portfolio, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")

    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")

        if not shares or not shares.isdigit():
            return apology("Invalid number of shares", 400)

        shares = int(shares)

        quote = lookup(symbol)
        if not quote:
            return apology("Invalid symbol", 400)
        if shares < 1:
            return apology("Invalid number of shares", 400)

        username = session["user_id"]
        user = db.execute("SELECT * FROM users WHERE id = :id", id=username)[0]
        username = user["username"]

        # Calculate the total cost of the purchase
        price_per_share = float(quote["price"])
        total_cost = shares * price_per_share

        if user["cash"] < total_cost:
            return apology("Insufficient funds", 400)

        # Update the purchases table
        db.execute("INSERT INTO purchases (username, symbol, shares, price, total_price, transaction_time) VALUES (:username, :symbol, :shares, :price, :total_price, :transaction_time)",
                   username=username,
                   symbol=symbol,
                   shares=shares,
                   price=price_per_share,
                   total_price=total_cost,
                   transaction_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Update the user's cash
        updated_cash = float(user["cash"]) - float(total_cost)
        username = user["username"]  # Get the username from the user variable

        # Update the user's cash in the database
        db.execute("UPDATE users SET cash = :updated_cash WHERE username = :username",
                updated_cash=updated_cash,
                username=username)

        return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    username = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = :id", id=username)[0]
    username = user["username"]

    portfolio = db.execute("""SELECT * FROM purchases WHERE username= :username""", username=username)

    return render_template("history.html", portfolio=portfolio)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")

    else:
        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)
        if not quote:
            return apology("invalid symbol", 400)
        return render_template("quoted.html", quote=quote)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check if the name already exists
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        if len(rows) != 0:
            return apology("username already exists", 400)

        if not username or not password or not confirmation:
            return apology("provide username and/or password", 400)

        if password != confirmation:
            return apology("check password again",400)

        # Hash the password before storing it in the database
        hashed_password = generate_password_hash(password)
        # Store the user in the database
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=hashed_password)

        # Automatically log in the user after registration
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=username)
        session["user_id"] = rows[0]["id"]

        return redirect("/")

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    username = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = :id", id=username)[0]
    username = user["username"]

    rows = db.execute("""
        SELECT symbol, SUM(shares) as total_shares
        FROM purchases
        WHERE username = :username
        GROUP BY symbol
        HAVING total_shares > 0
    """,username=username)

    symbols = [row['symbol'] for row in rows]

    if request.method == "GET":
        return render_template("sell.html", symbols=symbols)


    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("missing symbol", 400)
        if not shares or shares == 0:
            return apology("missing shares", 400)

        quote = lookup(symbol)

        portfolio = db.execute("""
            SELECT symbol, SUM(shares) as total_shares, SUM(total_price) as total_price
            FROM purchases
            WHERE username = :username AND symbol = :symbol
            GROUP BY symbol
        """, username=username, symbol=symbol)


        # Check if the user has enough shares to sell
        number_of_shares = int(portfolio[0]["total_shares"])
        shares = int(shares)
        if number_of_shares < shares:
            return apology("too many shares", 400)

        # update cash owned by the user
        # Calculate the total cost of the purchase
        shares = -shares
        price_per_share = float(quote["price"])
        total_cost = shares * price_per_share

        # Update the purchases table
        db.execute("INSERT INTO purchases (username, symbol, shares, price, total_price, transaction_time) VALUES (:username, :symbol, :shares, :price, :total_price, :transaction_time)",
                   username=username,
                   symbol=symbol,
                   shares=shares,
                   price=price_per_share,
                   total_price=total_cost,
                   transaction_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Update the user's cash
        updated_cash = float(user["cash"]) - float(total_cost)
        username = user["username"]  # Get the username from the user variable

        # Update the user's cash in the database
        db.execute("UPDATE users SET cash = :updated_cash WHERE username = :username",
                updated_cash=updated_cash,
                username=username)

    return redirect("/")
