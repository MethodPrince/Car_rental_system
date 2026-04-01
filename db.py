# db.py
from pymongo import MongoClient
import hashlib

# --- MongoDB Connection ---
connection_string = "mongodb+srv://admin:admin123@cluster0.y4vmdpb.mongodb.net/?appName=Cluster0"
client = MongoClient(connection_string)

# --- Database and collections ---
db = client["car_rental_db"]
cars_collection = db["cars"]
users_collection = db["users"]
customers_collection = db["customers"]

# --- CAR FUNCTIONS ---
def add_car(car):
    return cars_collection.insert_one(car)

def get_all_cars():
    return list(cars_collection.find())

def get_available_cars(make=None):
    query = {}
    if make:
        query["make"] = make
    cars = list(cars_collection.find(query))
    available = []
    for car in cars:
        rented = False
        for rental in car.get("rentals", []):
            if rental.get("returned_on") is None:
                rented = True
                break
        if not rented:
            available.append(car)
    return available

# Get distinct makes for dropdown
def get_car_makes():
    makes = cars_collection.distinct("make")
    return sorted([m for m in makes if m])

# Get specific car by ID
def get_car(car_id):
    return cars_collection.find_one({"car_id": car_id})

# Delete car by ID
def delete_car(car_id):
    return cars_collection.delete_one({"car_id": car_id})

# Rent a car (with customer info) only if not currently rented
def rent_car(car_id, customer_info, rented_on):
    rental = {
        "customer_info": customer_info,
        "rented_on": rented_on,
        "returned_on": None
    }
    return cars_collection.update_one(
        {
            "car_id": car_id,
            "$nor": [{"rentals": {"$elemMatch": {"returned_on": None}}}]
        },
        {"$push": {"rentals": rental}}
    )

# Return a car
def return_car(car_id, customer_id, returned_on):
    return cars_collection.update_one(
        {"car_id": car_id, "rentals.customer_info.id_number": customer_id, "rentals.returned_on": None},
        {"$set": {"rentals.$.returned_on": returned_on}}
    )

# --- USER/ADMIN FUNCTIONS ---
def add_user(user):
    if "password" in user:
        user["password"] = hashlib.sha256(user["password"].encode()).hexdigest()
    return users_collection.insert_one(user)

def get_user(username):
    return users_collection.find_one({"username": username})

# --- CUSTOMER FUNCTIONS ---
def add_customer(customer):
    return customers_collection.insert_one(customer)

def get_all_customers():
    return list(customers_collection.find())

# --- AGGREGATION / REPORT ---
def rental_report():
    pipeline = [
        {"$unwind": "$rentals"},
        {"$project": {
            "car_id": 1,
            "make": 1,
            "model": 1,
            "customer_id": "$rentals.customer_info.id_number",
            "customer_name": "$rentals.customer_info.name",
            "rented_on": "$rentals.rented_on",
            "returned_on": "$rentals.returned_on"
        }}
    ]
    return list(cars_collection.aggregate(pipeline))