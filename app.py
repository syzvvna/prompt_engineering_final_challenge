# app.py (Flask Backend)
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from threading import Lock

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Thread-safe in-memory storage for tasks
tasks = []
current_id = 1
tasks_lock = Lock()

# Task model
class Task:
    def __init__(self, id, description, completed=False):
        self.id = id
        self.description = description
        self.completed = completed
        self.date_created = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'completed': self.completed,
            'date_created': self.date_created
        }

# Helper function for error responses
def error_response(message, status_code):
    return jsonify({'error': message}), status_code

# Routes
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    try:
        with tasks_lock:
            return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        return error_response('Failed to fetch tasks', 500)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return error_response('Description is required.', 400)
        
        description = data['description'].strip()
        if not description:
            return error_response('Description cannot be empty.', 400)
        
        with tasks_lock:
            global current_id
            task = Task(current_id, description)
            tasks.append(task)
            current_id += 1
            
            return jsonify(task.to_dict()), 201
    except Exception as e:
        return error_response('Failed to create task', 500)

@app.route('/api/tasks/<int:task_id>/complete', methods=['PATCH'])
def toggle_task_completion(task_id):
    """Toggle task completion status"""
    try:
        with tasks_lock:
            task = next((t for t in tasks if t.id == task_id), None)
            
            if not task:
                return error_response('Task not found.', 404)
            
            task.completed = not task.completed
            return jsonify(task.to_dict())
    except Exception as e:
        return error_response('Failed to update task', 500)

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        with tasks_lock:
            global tasks
            task = next((t for t in tasks if t.id == task_id), None)
            
            if not task:
                return error_response('Task not found.', 404)
            
            tasks = [t for t in tasks if t.id != task_id]
            return jsonify({'message': 'Task deleted successfully.'})
    except Exception as e:
        return error_response('Failed to delete task', 500)

if __name__ == '__main__':
    app.run(debug=True)