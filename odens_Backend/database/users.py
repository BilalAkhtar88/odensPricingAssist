# This is a simple mock DB. Replace with actual DB in production.
users_db = {}

def get_user(email: str):
    return users_db.get(email)

def create_user(email: str, hashed_password: str):
    users_db[email] = {"email": email, "hashed_password": hashed_password}
    return users_db[email]
