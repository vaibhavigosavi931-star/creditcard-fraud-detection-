import argparse
import getpass
import re

from .auth import hash_password
from .database import create_user, init_db


def main():
    parser = argparse.ArgumentParser(description="Create a Credit Risk Lab admin user")
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    password = getpass.getpass("Admin password: ")
    if len(password) < 8:
        raise SystemExit("Password must be at least 8 characters.")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", args.email):
        raise SystemExit("Invalid email address.")
    init_db()
    create_user(args.username, args.email, hash_password(password), role="admin")
    print(f"Admin user created: {args.username}")


if __name__ == "__main__":
    main()