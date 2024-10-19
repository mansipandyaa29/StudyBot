from application import app, db 

# Create the database and tables
with app.app_context():
    db.create_all()