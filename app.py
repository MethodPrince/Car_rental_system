from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.utils import secure_filename
from db import add_car, get_all_cars, get_available_cars, get_car_makes, rent_car, return_car, rental_report, add_customer, get_all_customers, get_user, get_car, delete_car
import hashlib
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- LOGIN (Admin only) ---
@app.route("/")
def home():
    return render_template("home.html")

# --- LOGIN (Admin only) ---
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = get_user(username)
        if user and user.get("role") == "admin":
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            if user.get("password") == hashed_pw:
                session["username"] = username
                session["role"] = "admin"
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
    if "username" not in session or session.get("role") != "admin":
        return redirect("/")
    cars = get_all_cars()
    customers = get_all_customers()
    report = rental_report()
    return render_template("admin.html", cars=cars, customers=customers, report=report)

# --- DELETE CAR ---
@app.route("/delete_car/<car_id>", methods=["POST"])
def delete_car_route(car_id):
    if "username" not in session or session.get("role") != "admin":
        return redirect("/")
    delete_car(car_id)
    return redirect("/admin")

# --- ADD CAR ---
@app.route("/add_car", methods=["POST"])
def add_car_route():
    if "username" not in session or session.get("role") != "admin":
        return redirect("/")

    image_filename = ""
    image_file = request.files.get("image")
    if image_file and image_file.filename:
        uploads_dir = os.path.join(app.root_path, "static", "images")
        os.makedirs(uploads_dir, exist_ok=True)
        image_filename = secure_filename(image_file.filename)
        image_path = os.path.join(uploads_dir, image_filename)
        image_file.save(image_path)

    car = {
        "car_id": request.form["car_id"],
        "make": request.form["make"],
        "model": request.form["model"],
        "year": int(request.form["year"]),
        "features": [f.strip() for f in request.form.get("features", "").split(",") if f.strip()],
        "image": image_filename,
        "rentals": []
    }
    add_car(car)
    return redirect("/admin")

# --- ADD CUSTOMER ---
@app.route("/add_customer", methods=["POST"])
def add_customer_route():
    if "username" not in session or session.get("role") != "admin":
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
    if "username" not in session or session.get("role") != "admin":
        return redirect("/")
    returned_on = request.form["returned_on"]
    return_car(car_id, customer_id, returned_on)
    return redirect("/admin")

# --- PUBLIC PAGE: Available Cars ---
@app.route("/cars")
def public_cars():
    selected_make = request.args.get("make", "")
    available_cars = get_available_cars(selected_make) if selected_make else get_available_cars()
    makes = get_car_makes()
    return render_template("user.html", cars=available_cars, makes=makes, selected_make=selected_make)

# --- BOOK CAR PAGE ---
@app.route("/book_car/<car_id>")
def book_car(car_id):
    car = get_car(car_id)
    if not car:
        return "Car not found.", 404
    active = any(rental.get("returned_on") is None for rental in car.get("rentals", []))
    if active:
        return "This car is already rented. Please select another car.", 409
    return render_template("booking.html", car=car)

# --- CONFIRM BOOKING ---
@app.route("/confirm_booking/<car_id>", methods=["POST"])
def confirm_booking(car_id):
    car = get_car(car_id)
    if not car:
        return "Car not found.", 404
    customer_info = {
        "name": request.form["name"],
        "phone": request.form["phone"],
        "id_number": request.form["id_number"]
    }
    rented_on = request.form["rented_on"]
    result = rent_car(car_id, customer_info, rented_on)
    if result.modified_count == 0:
        return "This car is already rented. Please choose another.", 409
    return render_template("confirm.html", car=car, customer=customer_info, rented_on=rented_on)

# --- RENT CAR (Public user) ---
@app.route("/rent_car/<car_id>", methods=["POST"])
def rent_car_public(car_id):
    customer_info = {
        "name": request.form["name"],
        "phone": request.form["phone"],
        "id_number": request.form["id_number"]
    }
    rented_on = request.form["rented_on"]
    car = get_car(car_id)
    if not car:
        return "Car not found.", 404

    result = rent_car(car_id, customer_info, rented_on)
    if result.modified_count == 0:
        return "This car is already rented. Please choose another.", 409

    return redirect("/cars")

if __name__ == "__main__":

    app.run(debug=True)