
import os
from app import app, db, User

def migrate_passwords():
    """
    This script migrates plain text passwords from the old 'password' column
    to hashed passwords in the new 'password_hash' column.
    """
    with app.app_context():
        # First, ensure the new column exists in your database.
        # You may need to add it manually if it doesn't exist.
        # Example SQL command: ALTER TABLE users ADD COLUMN password_hash VARCHAR(256);
        print("Starting password migration...")

        users_to_migrate = User.query.filter(User.password != None).all()

        if not users_to_migrate:
            print("No users with plain text passwords found to migrate.")
            return

        print(f"Found {len(users_to_migrate)} user(s) to migrate.")

        for user in users_to_migrate:
            # Check if there is a password to migrate and if it hasn't been hashed already
            if user.password and not user.password.startswith('pbkdf2:sha256'):
                print(f"Migrating password for user: {user.userID}")
                user.set_password(user.password)
                # It's safer to nullify the old password field after migration
                user.password = None
        
        # Commit all the changes to the database
        db.session.commit()
        print("Password migration complete.")
        print("You should now manually delete the old 'password' column from your 'users' table.")

if __name__ == '__main__':
    # Before running, you might need to temporarily rename the `password_hash` field
    # in your models.py to `password` if you haven't updated the database schema yet,
    # run the migration, and then change it back.
    # A safer approach is to add the new column first.
    # This script assumes the `password` and `password_hash` columns co-exist.
    
    # To make this script work with the current models.py, you first need to add
    # the old password column back to the User model temporarily.
    
    # 1. Open models.py
    # 2. Add this line back to the User class:
    #    password = db.Column(db.String(200), nullable=True)
    # 3. Run this script: python migrate_passwords.py
    # 4. Remove the line from models.py again.
    
    # This process is delicate. Make sure you have a backup of your database.
    
    print("This script is a template. Please read the instructions within the script before running.")

