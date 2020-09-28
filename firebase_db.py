import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate('firebase_adminsdk.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://discord-bot-2ae41.firebaseio.com/'
})

# Get a database reference to our posts
ref = db.reference('fechas/parciales')

# Read the data at the posts reference (this is a blocking operation)
print(ref.get())