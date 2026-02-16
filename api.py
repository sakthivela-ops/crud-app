"""
Flask API for CRUD application
Serves data from MySQL users and favourite_sports tables
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    "user": "sakthivel",
    "password": "Qwerty@1234",
    "host": "127.0.0.1",
    "port": 3306,
    "database": "sports"
}


def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def close_db_connection(conn):
    """Close database connection"""
    if conn:
        conn.close()


@app.route('/api/users/search', methods=['GET'])
def search_users():
    """Search users by username"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({"error": "Search query required"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Search for users by username
        cursor.execute(
            "SELECT user_id, username, email, phone_number FROM users WHERE username LIKE %s",
            (f"%{query}%",)
        )
        users = cursor.fetchall()
        
        # For each user, get their favorite sports
        for user in users:
            cursor.execute(
                "SELECT sport_name FROM favourite_sports WHERE user_id = %s",
                (user['user_id'],)
            )
            sports = [row['sport_name'] for row in cursor.fetchall()]
            user['sports'] = sports
        
        cursor.close()
        return jsonify(users), 200
    
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        close_db_connection(conn)


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user with their favorite sports"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get user
        cursor.execute(
            "SELECT user_id, username, email, phone_number FROM users WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        
        if not user:
            cursor.close()
            return jsonify({"error": "User not found"}), 404
        
        # Get user's favorite sports
        cursor.execute(
            "SELECT sport_name FROM favourite_sports WHERE user_id = %s",
            (user_id,)
        )
        sports = [row['sport_name'] for row in cursor.fetchall()]
        user['sports'] = sports
        
        cursor.close()
        return jsonify(user), 200
    
    except Error as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        close_db_connection(conn)


@app.route('/api/create', methods=['POST'])
def create_user():
    """Create a new user with their favorite sports"""
    # Get form data
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    sports = request.form.getlist('sports')
    
    # Validate required fields
    if not name or not email or not phone:
        return jsonify({"error": "Name, email, and phone number are required"}), 400
    
    # Validate phone number is 10 digits
    if not phone.isdigit() or len(phone) != 10:
        return jsonify({"error": "Phone number must be exactly 10 digits"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Insert user into users table
        cursor.execute(
            "INSERT INTO users (username, email, phone_number) VALUES (%s, %s, %s)",
            (name, email, phone)
        )
        
        # Get the last inserted user_id
        user_id = cursor.lastrowid
        
        # Insert favorite sports
        if sports:
            for sport in sports:
                cursor.execute(
                    "INSERT INTO favourite_sports (user_id, sport_name) VALUES (%s, %s)",
                    (user_id, sport)
                )
        
        # Commit the transaction
        conn.commit()
        
        cursor.close()
        return jsonify({
            "message": "User created successfully",
            "user_id": user_id,
            "username": name,
            "email": email,
            "phone_number": phone,
            "sports": sports
        }), 201
    
    except Error as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    finally:
        close_db_connection(conn)


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user and their favorite sports"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "User not found"}), 404
        
        # Delete sports first (foreign key constraint)
        cursor.execute("DELETE FROM favourite_sports WHERE user_id = %s", (user_id,))
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        return jsonify({"message": "User deleted successfully"}), 200
    
    except Error as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    finally:
        close_db_connection(conn)


@app.route('/api/users/<int:user_id>/sports', methods=['PUT'])
def update_user_sports(user_id):
    """Update user's favorite sports"""
    # Get sports list from request
    sports = request.form.getlist('sports')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": "User not found"}), 404
        
        # Delete existing sports
        cursor.execute("DELETE FROM favourite_sports WHERE user_id = %s", (user_id,))
        
        # Insert new sports
        if sports:
            for sport in sports:
                cursor.execute(
                    "INSERT INTO favourite_sports (user_id, sport_name) VALUES (%s, %s)",
                    (user_id, sport)
                )
        
        conn.commit()
        cursor.close()
        return jsonify({
            "message": "Sports updated successfully",
            "user_id": user_id,
            "sports": sports
        }), 200
    
    except Error as e:
        conn.rollback()
        cursor.close()
        return jsonify({"error": str(e)}), 500
    
    finally:
        close_db_connection(conn)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    conn = get_db_connection()
    if conn:
        close_db_connection(conn)
        return jsonify({"status": "healthy"}), 200
    else:
        return jsonify({"status": "unhealthy", "error": "Cannot connect to database"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Run on all network interfaces (0.0.0.0) so it's accessible from other devices
    # For production with nginx, ensure CORS is properly configured
    app.run(host='0.0.0.0', port=5000, debug=False)
