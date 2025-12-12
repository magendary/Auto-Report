# Environment Configuration

## Backend Configuration

Create a `.env` file in the backend directory:

```bash
# Flask Configuration
FLASK_ENV=development  # or 'production'
FLASK_DEBUG=True       # Set to False in production
FLASK_HOST=0.0.0.0     # Use 127.0.0.1 in production
FLASK_PORT=5000

# Data Directory
DATA_DIR=..

# Reports Directory
REPORTS_DIR=reports
```

## Frontend Configuration

Create a `.env` file in the frontend directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:5000/api
```

## Production Deployment

For production deployment:

1. **Backend**:
   ```bash
   # Set environment variables
   export FLASK_ENV=production
   export FLASK_DEBUG=False
   
   # Use a production WSGI server
   pip install gunicorn
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   ```

2. **Frontend**:
   ```bash
   # Build for production
   npm run build
   
   # Serve with nginx or similar
   # Point to the dist/ directory
   ```

3. **Security Checklist**:
   - [ ] Disable Flask debug mode
   - [ ] Use environment variables for configuration
   - [ ] Set up proper CORS origins (not *)
   - [ ] Use HTTPS in production
   - [ ] Implement rate limiting
   - [ ] Add authentication if needed
   - [ ] Set up proper logging
   - [ ] Use a production database (if applicable)

## Notes

- The default configuration is for **development only**
- Never expose the debug server to the internet
- Always use environment variables for sensitive configuration
- Review all security settings before production deployment
