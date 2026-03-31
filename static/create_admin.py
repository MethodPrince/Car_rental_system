import os
import sys

# Add project root to sys.path so we can import db when running from the root folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import add_user

admin_user = {
    "username": "Method123",
    "role": "admin",
    "password": "Method@013"
}

add_user(admin_user)
print("Admin account created!")