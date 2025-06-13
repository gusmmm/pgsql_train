# Paper DB Manager Frontend

A React-based web application for managing and visualizing your PostgreSQL database containing scientific paper metadata and processing pipeline information.

## 🏗️ Architecture

This frontend consists of two main components:

- **Backend API** (`/api/`): Flask-based REST API that connects to PostgreSQL
- **Frontend App** (`/src/`): React application with Material-UI components

## 📋 Prerequisites

Before starting, ensure you have:

1. **Node.js** (version 16 or higher)
2. **Python** (version 3.8 or higher)
3. **PostgreSQL database** running and accessible
4. **Environment variables** configured in the project root `.env` file

### Required Environment Variables

Your project root `.env` file should contain:

```env
# PostgreSQL Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=8700
POSTGRES_DB=thedb
POSTGRES_USER=theuser
POSTGRES_PASSWORD=thepassword

# Google AI API Key (for paper processing)
GOOGLE_API_KEY=your_google_api_key_here
```

## 🚀 Quick Start

### 1. Start the Backend API

```bash
# Navigate to the API directory
cd /path/to/your/project/frontend/api

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Linux/macOS
# OR on Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start the Flask API server
python main.py
```

The API will start on `http://localhost:5001`

**Alternative method using Flask CLI:**
```bash
export FLASK_APP=main.py
flask run --port 5001
```

### 2. Start the Frontend App

Open a **new terminal** and run:

```bash
# Navigate to the frontend directory
cd /path/to/your/project/frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The React app will start on `http://localhost:3000` and automatically open in your browser.

## 🔧 API Endpoints

The Flask backend provides these endpoints:

- `GET /api/db/status` - Check database connection status
- `GET /api/db/schemas` - List all available schemas
- `GET /api/db/schema/<schema_name>/details` - Get tables, views, and functions for a schema

## 🎯 Features

### Current Features

- **Database Status Monitoring**: Real-time connection status with host/port information
- **Schema Browser**: Navigate through database schemas with a clean sidebar interface
- **Table/View/Function Listing**: View all objects within each schema
- **Responsive Design**: Material-UI components with a modern, clean interface
- **Error Handling**: Comprehensive error reporting and user feedback

### Planned Features

- Table data preview and querying
- Paper processing pipeline controls
- Real-time processing status updates
- Data visualization and statistics
- User authentication and access control

## 🛠️ Development

### Project Structure

```
frontend/
├── api/                      # Flask backend
│   ├── main.py              # API endpoints and database connections
│   ├── requirements.txt     # Python dependencies
│   └── venv/               # Virtual environment (created locally)
├── public/                  # React static assets
│   ├── index.html          # HTML template
│   └── manifest.json       # PWA manifest
├── src/                     # React source code
│   ├── components/         # Reusable UI components (future)
│   ├── services/           # API service layer
│   │   └── apiService.js   # Axios-based API client
│   ├── App.js              # Main application component
│   ├── index.js            # React entry point
│   └── index.css           # Global styles
├── package.json            # Node.js dependencies and scripts
└── README.md              # This file
```

### Backend API Dependencies

```
Flask==2.3.3
psycopg2-binary==2.9.7
python-dotenv==1.0.0
flask-cors==4.0.0
```

### Frontend Dependencies

Key dependencies include:
- React 18.3.1
- Material-UI 5.15.18
- Axios 1.7.2
- React Router 6.23.1

## 🐛 Troubleshooting

### Common Issues

1. **"Database connection failed"**
   - Ensure PostgreSQL is running
   - Check your `.env` file has correct database credentials
   - Verify the database is accessible from your machine

2. **"Module not found" errors**
   - Run `npm install` in the frontend directory
   - Run `pip install -r requirements.txt` in the api directory

3. **CORS errors in browser**
   - The Flask API includes CORS headers, but if you see issues, ensure both servers are running on the expected ports (3000 for React, 5001 for Flask)

4. **Port already in use**
   - Change the Flask port: `python main.py` (edit main.py to use a different port)
   - Change the React port: `PORT=3001 npm start`

### API Connection Issues

If the frontend can't connect to the API:

1. Verify the Flask API is running: `curl http://localhost:5001/api/db/status`
2. Check the API base URL in `src/services/apiService.js`
3. Ensure both frontend and backend are running simultaneously

## 📝 Logging and Debugging

- **Flask API**: Logs appear in the terminal where you started `python main.py`
- **React App**: Open browser developer tools (F12) to see console logs and network requests
- **Database Queries**: The Flask API logs database connection attempts and errors

## 🔐 Security Notes

- The `.env` file contains sensitive database credentials and should not be committed to version control
- The Flask API runs in debug mode for development - disable this for production
- CORS is enabled for local development - configure appropriately for production deployment

## 📚 Next Steps

To extend this application:

1. **Add Table Data Views**: Implement components to display table contents
2. **Integrate Processing Pipeline**: Add controls for running paper processing jobs
3. **Add Authentication**: Implement user login and access control
4. **Add Data Visualization**: Charts and graphs for database statistics
5. **Implement Real-time Updates**: WebSocket connections for live status updates

## 🤝 Contributing

When making changes:

1. Follow the existing code structure and patterns
2. Test both API endpoints and React components
3. Update this README if you add new features or dependencies
4. Ensure the `.gitignore` file excludes sensitive files and build artifacts

---

For questions or issues, refer to the main project documentation or create an issue in the project repository.
