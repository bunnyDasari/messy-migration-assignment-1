from flask import Flask, request, jsonify
import sqlite3
import json
import hashlib

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    return jsonify({"message": "User Management System"})

@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")  # Don't return passwords
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(users), 200
    except Exception:
        return jsonify({"error": "Failed to retrieve users"}), 500

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        if not user_id.isdigit():
            return jsonify({"error": "Invalid user ID"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return jsonify(dict(user)), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception:
        return jsonify({"error": "Failed to retrieve user"}), 500

@app.route('/users', methods=['POST'])
def create_user():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        
        if not all(key in data for key in ['name', 'email', 'password']):
            return jsonify({"error": "Missing required fields"}), 400
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = hash_password(data['password'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
       
        if existing_user:
           conn.close()
           return jsonify({"error": "User already exists"}), 409
        else:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                         (name, email, password))
            conn.commit()
            conn.close()
            
            return jsonify({"message": "User created"}), 201
            
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400
    except Exception:
        return jsonify({"error": "Failed to create user"}), 500

@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        if not user_id.isdigit():
            return jsonify({"error": "Invalid user ID"}), 400
            
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        name = data.get('name', '').strip() if data.get('name') else None
        email = data.get('email', '').strip().lower() if data.get('email') else None
        
        if not name and not email:
            return jsonify({"error": "At least name or email required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({"error": "User not found"}), 404
        
        update_parts = []
        params = []
        
        if name:
            update_parts.append("name = ?")
            params.append(name)
        if email:
            update_parts.append("email = ?")
            params.append(email)
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(update_parts)} WHERE id = ?"
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return jsonify({"message": "User updated"}), 200
        
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400
    except Exception:
        return jsonify({"error": "Failed to update user"}), 500

@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        if not user_id.isdigit():
            return jsonify({"error": "Invalid user ID"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "User not found"}), 404
        
        conn.commit()
        conn.close()
        return jsonify({"message": "User deleted"}), 200
        
    except Exception:
        return jsonify({"error": "Failed to delete user"}), 500

@app.route('/search', methods=['POST'])
def search_users():
    name = request.json.get('name')
    
    if not name:
        return jsonify({"error": "Please provide a name parameter"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, email FROM users WHERE name LIKE ?', (f'%{name}%',))
    rows = cursor.fetchall()
  
    users = []
    for row in rows:
        users.append({
            'id': row[0],
            'name': row[1],
            'email': row[2]
        })
    
    conn.close()
    return jsonify(users), 200

@app.route('/login', methods=['POST'])
def login():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        
        if not all(key in data for key in ['email', 'password']):
            return jsonify({"error": "Email and password required"}), 400
        
        email = data['email'].strip().lower()
        password = hash_password(data['password'])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return jsonify({"status": "success", "user_id": user[0]}), 200
        else:
            return jsonify({"status": "failed", "error": "Invalid credentials"}), 401
            
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400
    except Exception:
        return jsonify({"error": "Login failed"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)