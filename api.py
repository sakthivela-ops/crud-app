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


@app.route('/api/users', methods=['GET'])
def get_all_users():
    """Get all users with their favorite sports"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Get all users
        cursor.execute("SELECT user_id, username, email, phone_number FROM users")
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


@app.route('/api/sports', methods=['GET'])
def get_all_sports():
    """Get all sports from all users"""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT DISTINCT fs.sport_name, fs.user_id, u.username 
               FROM favourite_sports fs 
               JOIN users u ON fs.user_id = u.user_id"""
        )
        sports = cursor.fetchall()
        cursor.close()
        return jsonify(sports), 200
    
    except Error as e:
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
    # Run on localhost:5000
    # For production with nginx, ensure CORS is properly configured
    app.run(host='127.0.0.1', port=5000, debug=False)
