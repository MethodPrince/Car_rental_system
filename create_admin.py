import os
import sys

# Ensure the project root is on sys.path, so db can be imported when executed from root.
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from db import add_user, get_user

admin_user = {
    "username": "Method123",
    "role": "admin",
    "password": "Method@013"
}

if get_user(admin_user['username']):
    print(f"Admin user '{admin_user['username']}' already exists.")
else:
    add_user(admin_user)
    print("Admin account created!")