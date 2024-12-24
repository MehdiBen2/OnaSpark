from app import app, db, User
from waitress import serve
import os

# Create default admin user if it doesn't exist
with app.app_context():
    try:
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                role='Admin'
            )
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
            print("\nDefault admin credentials:")
            print("Username: admin")
            print("Password: admin")
            print("Please change these credentials after first login.")
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")

if __name__ == "__main__":
    # Get port from environment variable or use 5000 as default
    port = int(os.environ.get("PORT", 5000))
    print(f"\n{'='*50}")
    print(f"Server is running at http://localhost:{port}")
    print(f"{'='*50}\n")
    serve(app, host='localhost', port=port, url_scheme='http')
