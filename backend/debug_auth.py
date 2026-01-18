# debug_auth.py
from auth import verify_password, get_password_hash

# 1. The Hash from your database logs (I copied this from your message)
stored_hash = "$2b$12$CVb6KbaufGHpcr5yLVQtL.IQz5bM3meJiHNZM.j/qjJhIjRYfHl0a"

# 2. The Password you are trying to use
# REPLACE THIS with exactly what you are typing in the form
attempted_password = "string09011"

print(f"Testing password: '{attempted_password}'")
print(f"Against hash:     '{stored_hash}'")

# 3. The Moment of Truth
result = verify_password(attempted_password, stored_hash)

if result:
    print("\n✅ MATCH! The password is correct.")
    print("This means your API issue is likely hidden whitespace in the form input.")
else:
    print("\n❌ NO MATCH.")
    print("This means the password you are typing is NOT what is saved in the DB.")
    print("Let's see what the hash of your input SHOULD look like:")
    print(f"Correct hash for this password would be: {get_password_hash(attempted_password)}")