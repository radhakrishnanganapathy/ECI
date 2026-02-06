import sys
from database import SessionLocal, User

def update_user_role(username, new_role):
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        print(f"Error: User '{username}' not found.")
        db.close()
        return

    if new_role not in ['admin', 'user']:
        print(f"Error: Invalid role '{new_role}'. Choose 'admin' or 'user'.")
        db.close()
        return

    user.role = new_role
    db.commit()
    print(f"Successfully updated '{username}' to role: {new_role}")
    db.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python update_role.py <username> <role>")
        print("Example: python update_role.py john_doe admin")
    else:
        username = sys.argv[1]
        role = sys.argv[2].lower()
        update_user_role(username, role)
