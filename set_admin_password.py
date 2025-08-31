
from app import app, db, User

# The new password you want to set for the admin user
NEW_PASSWORD = 'admin123'

def set_admin_password():
    """Finds the 'admin' user and sets a new, hashed password."""
    with app.app_context():
        admin_user = User.query.filter_by(userID='admin').first()

        if admin_user:
            print(f"Found admin user: {admin_user.userID}. Setting new password...")
            admin_user.set_password(NEW_PASSWORD)
            db.session.commit()
            print(f"Password for 'admin' has been successfully reset to: {NEW_PASSWORD}")
        else:
            print("Error: Could not find a user with userID = 'admin'.")

if __name__ == '__main__':
    set_admin_password()
