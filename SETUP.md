# CRUD Application Setup Guide

## Overview
This application fetches user data and their favorite sports from a MySQL database and displays them through a web interface using Flask API and Nginx.

## Database Tables
- **users**: Fields - user_id (PRI), username, email, phone_number
- **favourite_sports**: Fields - favourite_id (PRI), user_id (FK), sport_name

## Components

### 1. Flask Backend API (api.py)

**Database Connection Details:**
- User: sakthivel
- Password: Qwerty@1234
- Host: 127.0.0.1
- Port: 3306
- Database: sports

**Available Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users` | GET | Get all users with their sports |
| `/api/users/search?q=<query>` | GET | Search users by username |
| `/api/users/<user_id>` | GET | Get specific user with sports |
| `/api/sports` | GET | Get all sports |
| `/api/health` | GET | Health check |

**Response Format:**
```json
{
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "phone_number": "1234567890",
    "sports": ["Cricket", "Football"]
}
```

### 2. Frontend (web-page/html/view_page.html)

The HTML page queries the Flask API for user data when you search for a username. It displays:
- User basic info (name, email, phone)
- List of interested sports
- Edit/Delete buttons for sports

**API Base URL:** Configured in JavaScript - change if deploying to different host:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

## Installation & Running

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt
```

### Run Flask API
```bash
# Development mode
python api.py

# Production mode (with gunicorn)
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 api:app
```

The API will be available at: `http://localhost:5000/api`

### Setup Nginx

1. **Update nginx.conf** - Replace `/path/to/your/crud-app` with your actual path

2. **Install nginx** (if not already installed):
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

3. **Copy configuration**:
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/crud-app
   sudo ln -s /etc/nginx/sites-available/crud-app /etc/nginx/sites-enabled/
   ```

4. **Test configuration**:
   ```bash
   sudo nginx -t
   ```

5. **Start/Reload nginx**:
   ```bash
   sudo systemctl start nginx
   # or reload if already running:
   sudo systemctl reload nginx
   ```

6. **Access the application**:
   - Open browser to `http://localhost/`
   - Search for a user by username
   - View their profile and sports

## Development vs Production

### Development
```bash
python api.py  # Runs on http://localhost:5000
# Update API_BASE_URL in view_page.html if using different port
```

### Production with Nginx
```bash
# Run Flask with gunicorn
gunicorn -w 4 -b 127.0.0.1:5000 api:app

# Nginx handles incoming requests on port 80 and proxies to Flask
```

## Troubleshooting

### Can't connect to database?
- Verify MySQL is running: `mysql -u sakthivel -pH -D sports`
- Check credentials in `api.py`
- Verify database name is "sports"

### CORS errors in browser console?
- Flask-CORS is already configured
- Nginx configuration includes CORS headers
- Update `API_BASE_URL` to match your deployment host

### API not responding?
- Check if Flask is running: `curl http://localhost:5000/api/health`
- Check Flask logs for errors
- Ensure port 5000 is not blocked by firewall

### Getting 404 on root path?
- Ensure `root /path/to/crud-app/web-page` in nginx.conf is correct
- Verify HTML structure matches the location blocks

## Files Overview

```
crud-app/
├── api.py                    # Flask REST API
├── requirements.txt          # Python dependencies
├── nginx.conf               # Nginx configuration
├── test.py                  # Original test script
└── web-page/
    ├── html/
    │   ├── view_page.html   # Search & display page
    │   ├── create_page.html # Create user
    │   └── edit_page.html   # Edit page
    └── css/
        ├── view.css         # Styles
        ├── main.css
        └── edit.css
```

## Next Steps

1. Start the Flask API
2. Configure and start Nginx
3. Access the application through your browser
4. Test the search functionality with existing usernames
