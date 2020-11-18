import cs50
import csv

from flask import Flask, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    """Redirects the index to /form """
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():
    """Returns the Name, House and Role from the form"""

    """Checking for missing data"""
    if not request.form.get("name") or not request.form.get("house") or not request.form.get("role"):
        return render_template("error.html", message="Please go back and input your details!")

    """Appending data to csv file"""
    file = open("survey.csv", "a")
    writer = csv.writer(file)
    writer.writerow([request.form.get("name"), request.form.get("house"), request.form.get("role")])
    file.close()
    return redirect("/sheet")


@app.route("/sheet", methods=["GET"])
def get_sheet():
    """Reading data from CSV and displaying to /sheet"""
    file = open("survey.csv", "r")
    reader = csv.reader(file)
    students = list(reader)
    return render_template("sheet.html", students=students)
