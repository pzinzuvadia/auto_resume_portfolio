# Deploying to Streamlit Cloud

This document contains step-by-step instructions for deploying the AI Portfolio Generator to Streamlit Cloud.

## Prerequisites

Before deploying to Streamlit Cloud, make sure you have:

1. A GitHub account to host your repository
2. An Anthropic API key for Claude AI
3. (Optional) A PostgreSQL database if you want persistent storage

## Deployment Steps

### 1. Fork or Push to GitHub

First, you need to have your code in a GitHub repository:

- Fork this repository to your GitHub account, or
- Create a new GitHub repository and push this code to it

### 2. Sign up for Streamlit Cloud

If you haven't already, sign up for a free Streamlit Cloud account at [https://streamlit.io/cloud](https://streamlit.io/cloud).

### 3. Create a New App

In the Streamlit Cloud dashboard:

1. Click on "New app"
2. Select your GitHub repository
3. In the "Main file path" field, enter: `streamlit_app.py`
4. Click "Advanced settings" to configure resources if needed
5. Click "Deploy"

### 4. Configure Secrets

After deployment, you need to add your secrets:

1. In the Streamlit Cloud dashboard, find your app
2. Click on the three dots (⋮) and select "Settings"
3. Click on "Secrets"
4. Add your secrets in TOML format:

```toml
ANTHROPIC_API_KEY = "your_anthropic_api_key_here"

# Only add these if you're using a PostgreSQL database
[postgres]
host = "your_db_host"
port = 5432
dbname = "your_db_name"
user = "your_db_user"
password = "your_db_password"
```

5. Click "Save"

### 5. Reboot the App

After adding secrets:

1. Go back to your app settings
2. Click "Reboot app"

### Troubleshooting

If your deployment is not working:

1. Check the app logs in the Streamlit Cloud dashboard
2. Verify that your secrets are configured correctly
3. Make sure the `streamlit_app.py` file has the correct port configurations
4. Ensure your database connection is properly configured (if using a database)

### Limitations

When deployed on Streamlit Cloud:

1. File uploads are limited to 200MB
2. The app may experience occasional restarts
3. Persistent storage requires an external database
4. Custom domains require a paid Streamlit Cloud plan

For more information, visit the [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud).