# Deploying Smart Fridge AI Dashboard on Render

This guide explains how to deploy the Smart Fridge AI Dashboard on Render.

## Option 1: Automatic Deployment with Blueprint

The easiest way to deploy is using the `render.yaml` blueprint included in this repository.

1. Fork this repository to your GitHub account
2. Log in to your [Render dashboard](https://dashboard.render.com)
3. Click the "New" button and select "Blueprint"
4. Connect your GitHub account if not already connected
5. Select your forked repository
6. Render will detect the `render.yaml` file and show services to be created
7. Click "Apply" to create and deploy the services
8. In the backend service settings, add your OpenAI API key as an environment variable:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key

After deployment, your services will be available at:
- Backend API: https://smart-fridge-backend.onrender.com
- Frontend Dashboard: https://smart-fridge-dashboard.onrender.com

## Option 2: Manual Deployment

If you prefer to deploy manually, follow these steps:

### Backend Deployment

1. Log in to your [Render dashboard](https://dashboard.render.com)
2. Click "New" and select "Web Service"
3. Connect your GitHub repository
4. Configure the web service:
   - **Name**: `smart-fridge-backend`
   - **Environment**: Python 3
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ALLOWED_ORIGINS`: The URL of your frontend (e.g., https://smart-fridge-dashboard.onrender.com)
6. Click "Create Web Service"

### Frontend Deployment

1. Return to your Render dashboard
2. Click "New" and select "Static Site"
3. Connect your GitHub repository
4. Configure the static site:
   - **Name**: `smart-fridge-dashboard`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `build`
5. Add environment variables:
   - `REACT_APP_API_URL`: The URL of your backend API (e.g., https://smart-fridge-backend.onrender.com/api)
6. Click "Create Static Site"

## Troubleshooting

If you encounter issues with the deployment:

1. Check the logs in your Render dashboard
2. Verify that environment variables are set correctly
3. Make sure your OpenAI API key is valid and has access to the required models
4. Check that the CORS settings are correctly configured

## Maintaining Your Deployment

- Render automatically deploys when you push changes to your GitHub repository
- You can disable auto-deploy in the service settings if needed
- Monitor your API usage to stay within free tier limits or adjust your plan as needed 