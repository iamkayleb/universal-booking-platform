from auth import get_password_hash

try:
    print("Attempting to hash 'string1234'...")
    hashed = get_password_hash("string1234")
    print("SUCCESS! Hash:", hashed)
except Exception as e:
    print("FAILED with error:", e)