import sys
import os

# Add the project root to sys.path to allow importing from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.utils.security import hash_password, verify_password
except ImportError as e:
    print(f"Error: Could not import security utilities. Make sure you are running this from the project root. {e}")
    sys.exit(1)

def main():
    print("--- Argon2 Password Hashing & Verification Tool ---")
    print("1. Hash a password")
    print("2. Verify a password against a hash")
    print("3. Exit")
    
    choice = input("\nSelect an option (1-3): ")
    
    if choice == '1':
        password = input("Enter password to hash: ")
        if not password:
            print("Password cannot be empty.")
            return
        hashed = hash_password(password)
        print(f"\nHashed Password:\n{hashed}")
        print("\nNote: Each time you hash the same password, the output will be different due to the random salt.")
        
    elif choice == '2':
        entered_hash = input("Enter the Argon2 hash: ").strip()
        password = input("Enter the password to verify: ")
        
        if not entered_hash or not password:
            print("Hash and password cannot be empty.")
            return
            
        is_valid = verify_password(password, entered_hash)
        
        if is_valid:
            print("\n[SUCCESS] Password matches the hash!")
        else:
            print("\n[FAILED] Password does NOT match the hash.")
            
    elif choice == '3':
        print("Exiting...")
        sys.exit(0)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    while True:
        try:
            main()
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            input("\nPress Enter to return to menu...")
