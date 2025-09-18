# CS QuizXverse - Render Deployment Guide

This guide will help you deploy your CS QuizXverse application to Render.

## Prerequisites

1. A GitHub account
2. A Render account (sign up at [render.com](https://render.com))
3. Your code pushed to a GitHub repository

## Deployment Steps

### 1. Prepare Your Repository

Make sure all the following files are in your repository root:

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `render.yaml` - Render configuration
- `gunicorn.conf.py` - Gunicorn configuration
- `Procfile` - Process file for Render
- `templates/` - HTML templates directory
- `static/` - CSS/JS static files directory
- `data/questions/` - JSON question files

### 2. Create a New Web Service on Render

1. Log in to your Render dashboard
2. Click "New +" and select "Web Service"
3. Connect your GitHub account if not already connected
4. Select your CS QuizXverse repository

### 3. Configure the Service

Use these settings:

- **Name**: `cs-quizxverse` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose the closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (root of repository)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --config gunicorn.conf.py app:app`

### 4. Environment Variables (Optional)

You can set these environment variables in the Render dashboard:

- `FLASK_ENV`: Set to `production` for production deployment
- `PORT`: Automatically set by Render (don't override)

### 5. Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Wait for the deployment to complete (usually 2-5 minutes)

### 6. Access Your Application

Once deployed, you'll get a URL like: `https://cs-quizxverse.onrender.com`

## File Descriptions

### `render.yaml`
Contains the service configuration for Render. This file tells Render how to build and run your application.

### `gunicorn.conf.py`
Production WSGI server configuration optimized for Render's free tier.

### `Procfile`
Process file that tells Render how to start your application.

### `requirements.txt`
Updated with `gunicorn` for production deployment.

## Troubleshooting

### Common Issues

1. **Build Fails**: Check that all dependencies are in `requirements.txt`
2. **App Won't Start**: Verify the start command in Render dashboard
3. **Static Files Not Loading**: Ensure `static/` directory is in the repository root
4. **Questions Not Loading**: Check that `data/questions/` directory and JSON files are present

### Logs

Check the Render dashboard logs for detailed error information:
1. Go to your service dashboard
2. Click on "Logs" tab
3. Look for error messages during build or runtime

### Health Check

Render automatically performs health checks on the root path (`/`). Make sure your Flask app serves content on this route.

## Free Tier Limitations

- Service sleeps after 15 minutes of inactivity
- 750 hours of usage per month
- Limited to 1 worker process
- Cold starts may take 30-60 seconds

## Upgrading to Paid Plans

For production use, consider upgrading to a paid plan for:
- Always-on service (no sleeping)
- More resources
- Better performance
- Custom domains

## Support

- Render Documentation: [render.com/docs](https://render.com/docs)
- Flask Documentation: [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- Gunicorn Documentation: [docs.gunicorn.org](https://docs.gunicorn.org/)

## Security Notes

- Never commit sensitive data like API keys to your repository
- Use environment variables for configuration
- The current setup is suitable for development and small-scale production use
