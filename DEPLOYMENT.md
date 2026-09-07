# Render Deployment Guide

This guide will help you deploy the Rural Land Survey application on Render.com.

## Prerequisites

- A Render.com account (free tier is sufficient)
- Git repository with your code
- The project files should be structured as follows:
  ```
  rural_land_survey/
  ├── app/
  ├── frontend/
  ├── requirements.txt
  ├── render.yaml
  └── other project files
  ```

## Deployment Steps

### 1. Push Code to GitHub

First, ensure your project is pushed to a GitHub repository:

```bash
git init
git add .
git commit -m "Initial commit for Render deployment"
git branch -M main
git remote add origin https://github.com/your-username/rural-land-survey.git
git push -u origin main
```

### 2. Connect to Render

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Select the `rural-land-survey` repository

### 3. Configure Deployment

Render will automatically detect the `render.yaml` file and configure the deployment. The configuration includes:

- **Runtime**: Python 3.11
- **Build Command**: Installs Python dependencies and builds the frontend
- **Start Command**: Runs the FastAPI app with Gunicorn
- **Database**: PostgreSQL database automatically created and linked
- **Environment Variables**: Auto-generated SECRET_KEY and configured DATABASE_URL

### 4. Manual Configuration (if needed)

If Render doesn't auto-detect the configuration, set these manually:

**Build Command:**
```bash
pip install -r requirements.txt && cd frontend && npm install && npm run build
```

**Start Command:**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT
```

**Environment Variables:**
- `PYTHON_VERSION`: `3.11`
- `DATABASE_URL`: (Will be provided by PostgreSQL database)
- `SECRET_KEY`: (Generate a secure random string)
- `LAND_DATA_PROVIDER`: `mock`
- `PORT`: `8000`

### 5. Database Setup

The `render.yaml` file automatically creates a PostgreSQL database. No manual setup is required. The database connection string will be automatically linked to the `DATABASE_URL` environment variable.

### 6. Monitor Deployment

After deploying, you can monitor:
- **Build Logs**: Watch the build process
- **Service Logs**: Monitor runtime logs
- **Database**: Check PostgreSQL status in the dashboard

## What Was Fixed

The following issues were addressed to enable Render deployment:

### 1. Database Configuration
- **Problem**: Original code used SQLite with file paths
- **Solution**: Updated database configuration to support PostgreSQL with connection pooling
- **File**: `app/core/database.py`

### 2. Render Configuration
- **Problem**: No `render.yaml` file existed
- **Solution**: Created comprehensive Render configuration with auto-scaling and database linking
- **File**: `render.yaml`

### 3. Frontend Integration
- **Problem**: Frontend not integrated with backend for production
- **Solution**: Added static file serving and SPA routing support
- **File**: `app/main.py`

### 4. Environment Variables
- **Problem**: No documentation for required environment variables
- **Solution**: Created environment variable documentation
- **File**: `ENVIRONMENT_VARIABLES.md`

## Troubleshooting

### Build Fails
- Check the build logs for specific errors
- Ensure all dependencies in `requirements.txt` are compatible
- Verify Node.js version is compatible with frontend dependencies

### Database Connection Issues
- Ensure PostgreSQL database is running
- Check that `DATABASE_URL` is correctly set
- Verify database connection pooling settings

### Frontend Not Loading
- Ensure frontend build completed successfully
- Check that `frontend/dist` directory exists
- Verify static file serving configuration

### Application Won't Start
- Check that Gunicorn can find the app module
- Verify Python version compatibility
- Ensure all environment variables are set

## Accessing Your Deployed App

Once deployed, you can access:
- **Application**: `https://your-app-name.onrender.com`
- **API Documentation**: `https://your-app-name.onrender.com/api/docs`
- **Alternative Docs**: `https://your-app-name.onrender.com/api/redoc`

## Post-Deployment Setup

After successful deployment:

1. **Test the API**: Visit `/api/docs` to test all endpoints
2. **Verify Database**: Check that database tables were created
3. **Test Frontend**: Navigate to the root URL to test the frontend
4. **Monitor Logs**: Regularly check logs for any issues

## Scaling Options

The free tier includes:
- 512 MB RAM
- 0.1 CPU
- Free PostgreSQL database (90 days)

For production, consider upgrading to:
- **Standard**: $7/month - 2 GB RAM, 1 CPU
- **Pro**: $25/month - 8 GB RAM, 4 CPUs

## Maintenance

### Updates
To update your deployed app:
1. Push changes to GitHub
2. Render automatically detects and redeploys
3. Monitor build logs for any issues

### Database Backups
Render automatically backs up PostgreSQL databases daily. You can also:
- Create manual backups via the dashboard
- Download backups for local testing

### Log Management
- Logs are retained for 7 days on free tier
- Upgraded plans have longer retention
- Consider external log aggregation for production

## Security Considerations

1. **SECRET_KEY**: Ensure this is properly generated and never committed
2. **Database**: Use strong passwords for PostgreSQL
3. **HTTPS**: Render automatically provides SSL certificates
4. **CORS**: Currently set to allow all origins - restrict in production
5. **API Keys**: Store any external API keys in environment variables

## Support

If you encounter issues:
1. Check Render's [documentation](https://render.com/docs)
2. Review this project's logs in the Render dashboard
3. Test locally with the same environment variables
4. Open an issue in the GitHub repository