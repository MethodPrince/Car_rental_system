# main.py
import tkinter as tk
from tkinter import messagebox
from db import add_car, get_all_cars, rent_car, rentals_count

# --- GUI Setup ---
root = tk.Tk()
root.title("Car Rental System")
root.geometry("800x500")

# ===== Layout =====
left_frame = tk.Frame(root)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

right_frame = tk.Frame(root)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# ===== FUNCTIONS =====

def insert_car():
    try:
        car = {
            "car_id": entry_id.get(),
            "make": entry_make.get(),
            "model": entry_model.get(),
            "year": int(entry_year.get()),
            "features": entry_features.get().split(","),
            "rentals": []
        }
        add_car(car)
        messagebox.showinfo("Success", "Car added!")
        show_cars()
    except:
        messagebox.showerror("Error", "Invalid input")

def show_cars():
    car_listbox.delete(0, tk.END)
    cars = get_all_cars()

    for car in cars:
        text = f"{car['car_id']} | {car['make']} {car['model']} | {car['year']}"
        car_listbox.insert(tk.END, text)

def rent_car_gui():
    car_id = entry_rent_car_id.get()
    customer_id = entry_customer_id.get()
    rented_on = entry_rented_on.get()

    rent_car(car_id, customer_id, rented_on)
    messagebox.showinfo("Success", "Car rented!")
    show_cars()

def show_rentals_report():
    report = rentals_count()
    text = ""

    for r in report:
        text += f"{r['car_id']} → Rentals: {r['num_rentals']}\n"

    messagebox.showinfo("Report", text)

# ===== LEFT SIDE (FORMS) =====

# Add Car
tk.Label(left_frame, text="Add Car", font=("Arial", 12, "bold")).pack()

entry_id = tk.Entry(left_frame)
entry_id.pack()
entry_id.insert(0, "Car ID")

entry_make = tk.Entry(left_frame)
entry_make.pack()
entry_make.insert(0, "Make")

entry_model = tk.Entry(left_frame)
entry_model.pack()
entry_model.insert(0, "Model")

entry_year = tk.Entry(left_frame)
entry_year.pack()
entry_year.insert(0, "Year")

entry_features = tk.Entry(left_frame)
entry_features.pack()
entry_features.insert(0, "Features")

tk.Button(left_frame, text="Add Car", command=insert_car).pack(pady=5)

# Rent Car
tk.Label(left_frame, text="Rent Car", font=("Arial", 12, "bold")).pack(pady=10)

entry_rent_car_id = tk.Entry(left_frame)
entry_rent_car_id.pack()
entry_rent_car_id.insert(0, "Car ID")

entry_customer_id = tk.Entry(left_frame)
entry_customer_id.pack()
entry_customer_id.insert(0, "Customer ID")

entry_rented_on = tk.Entry(left_frame)
entry_rented_on.pack()
entry_rented_on.insert(0, "Date")

tk.Button(left_frame, text="Rent Car", command=rent_car_gui).pack(pady=5)

# ===== RIGHT SIDE (DISPLAY) =====

tk.Label(right_frame, text="Cars", font=("Arial", 12, "bold")).pack()

car_listbox = tk.Listbox(right_frame)
car_listbox.pack(fill="both", expand=True)

tk.Button(right_frame, text="Refresh Cars", command=show_cars).pack(pady=5)
tk.Button(right_frame, text="Show Rentals Report", command=show_rentals_report).pack(pady=5)

# Load data at start
show_cars()

root.mainloop()