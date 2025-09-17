# CS Quizverse - Netlify Deployment Guide

This guide will help you deploy your CS Quizverse project to Netlify.

## Prerequisites

1. A Netlify account (free tier is sufficient)
2. Your project code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### Method 1: Deploy from Git Repository (Recommended)

1. **Connect to Netlify:**
   - Go to [netlify.com](https://netlify.com) and sign in
   - Click "New site from Git"
   - Choose your Git provider (GitHub, GitLab, or Bitbucket)
   - Select your CS Quizverse repository

2. **Configure Build Settings:**
   - Build command: `python build.py`
   - Publish directory: `dist`
   - Python version: `3.11` (will be set automatically)

3. **Deploy:**
   - Click "Deploy site"
   - Netlify will automatically build and deploy your site

### Method 2: Manual Deploy

1. **Build the project locally:**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Build static files
   python build.py
   ```

2. **Deploy to Netlify:**
   - Go to Netlify dashboard
   - Drag and drop the `dist` folder to deploy

## Project Structure for Netlify

```
CS_Quizverse/
├── netlify.toml              # Netlify configuration
├── build.py                  # Build script
├── requirements.txt          # Python dependencies
├── netlify/
│   └── functions/
│       └── api/
│           ├── __init__.py
│           └── questions.py  # API functions
├── dist/                     # Generated static files (created during build)
├── data/                     # Question data
├── static/                   # Static assets
├── templates/                # HTML templates
└── app.py                    # Original Flask app
```

## Configuration Files

### netlify.toml
- Configures build settings, redirects, and headers
- Sets up API function routing
- Handles SPA routing for client-side navigation

### build.py
- Generates static HTML files from Flask templates
- Copies static assets and data files
- Creates API data files for client-side consumption

### Netlify Functions
- `netlify/functions/api/questions.py` - Handles all API endpoints
- Provides serverless backend functionality
- Supports CORS for client-side requests

## Environment Variables

No environment variables are required for basic functionality. The application uses:
- Static question data from JSON files
- Client-side JavaScript for quiz functionality
- Netlify Functions for API endpoints

## Custom Domain (Optional)

1. Go to Site settings > Domain management
2. Add your custom domain
3. Configure DNS settings as instructed by Netlify
4. Enable HTTPS (automatic with Netlify)

## Monitoring and Updates

- **Automatic deployments:** Any push to your main branch triggers a new deployment
- **Build logs:** Available in the Netlify dashboard
- **Analytics:** Available in the Netlify dashboard (paid plans)
- **Forms:** Netlify Forms can be used if you need contact forms

## Troubleshooting

### Build Failures
- Check build logs in Netlify dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify Python version compatibility

### API Issues
- Check Netlify Functions logs
- Verify CORS headers in function responses
- Test API endpoints using browser developer tools

### Static File Issues
- Ensure `build.py` runs successfully locally
- Check that all static assets are copied to `dist` folder
- Verify file paths in templates

## Performance Optimization

- Static files are automatically cached by Netlify CDN
- Images and assets in `/static/` are cached for 1 year
- API responses are cached based on Netlify's edge caching

## Security

- HTTPS is automatically enabled
- Security headers are configured in `netlify.toml`
- No sensitive data is exposed in client-side code

## Support

For issues specific to:
- **Netlify deployment:** Check Netlify documentation
- **Project code:** Review the build logs and function logs
- **API functionality:** Test endpoints manually and check browser console
