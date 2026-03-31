from flask import Flask, render_template, request, redirect, session
from db import add_car, get_all_cars, get_available_cars, rent_car, return_car, rental_report, add_customer, get_all_customers, get_user
import hashlib

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- LOGIN (Admin only) ---
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_user(username)
        if user and user.get("role") == "admin":
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            if user.get("password") == hashed_pw:
                session["username"] = username
                return redirect("/admin")
        return "Invalid admin username or password!"
    return render_template("login.html")

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --- ADMIN DASHBOARD ---
@app.route("/admin")
def admin_dashboard():
    if "username" not in session:
        return redirect("/")
    cars = get_all_cars()
    customers = get_all_customers()
    report = rental_report()
    return render_template("admin.html", cars=cars, customers=customers, report=report)

# --- ADD CAR ---
@app.route("/add_car", methods=["POST"])
def add_car_route():
    if "username" not in session:
        return redirect("/")
    car = {
        "car_id": request.form["car_id"],
        "make": request.form["make"],
        "model": request.form["model"],
        "year": int(request.form["year"]),
        "features": request.form["features"].split(","),
        "rentals": []
    }
    add_car(car)
    return redirect("/admin")

# --- ADD CUSTOMER ---
@app.route("/add_customer", methods=["POST"])
def add_customer_route():
    if "username" not in session:
        return redirect("/")
    customer = {
        "customer_id": request.form["customer_id"],
        "name": request.form["name"]
    }
    add_customer(customer)
    return redirect("/admin")

# --- RETURN CAR ---
@app.route("/return_car/<car_id>/<customer_id>", methods=["POST"])
def return_car_route(car_id, customer_id):
    if "username" not in session:
        return redirect("/")
    returned_on = request.form["returned_on"]
    return_car(car_id, customer_id, returned_on)
    return redirect("/admin")

# --- PUBLIC PAGE: Available Cars ---
@app.route("/cars")
def public_cars():
    available_cars = get_available_cars()
    return render_template("user.html", cars=available_cars)

# --- RENT CAR (Public user) ---
@app.route("/rent_car/<car_id>", methods=["POST"])
def rent_car_public(car_id):
    customer_info = {
        "name": request.form["name"],
        "phone": request.form["phone"],
        "id_number": request.form["id_number"]
    }
    rented_on = request.form["rented_on"]
    rent_car(car_id, customer_info, rented_on)
    return redirect("/cars")

if __name__ == "__main__":
    app.run(debug=True)