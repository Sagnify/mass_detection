import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify

# Initialize Firebase
cred = credentials.Certificate('firebase/credentials.json')  # Path to your Firebase credentials file
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://citygrid-ef8e8-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Replace with your Firebase database URL
})

# Initialize Flask app
app = Flask(__name__)
 
# Route to handle POST requests for crowd data
@app.route('/api/crowd_data/', methods=['POST'])
def add_crowd_data():
    # Get JSON data from the request
    data = request.get_json()

    # Push data to Firebase Realtime Database
    ref = db.reference('crowd_data')  # 'crowd_data' is the key where data will be stored
    ref.push(data)

    return jsonify({"message": "Data saved successfully!"}), 201

# Route to handle GET requests for crowd data
@app.route('/api/crowd_data/', methods=['GET'])
def get_crowd_data():
    # Retrieve all crowd data from Firebase
    ref = db.reference('crowd_data')
    crowd_data = ref.get()

    return jsonify(crowd_data), 200

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
