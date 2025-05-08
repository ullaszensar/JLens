# JLens Deployment Guide

This guide will help you deploy the JLens application in various environments.

## Local Deployment

For local development and testing:

1. Install dependencies as described in README.md
2. Run the application with `streamlit run app.py`
3. Access the application at http://localhost:5000

## Server Deployment

### Prerequisites

- Python 3.8+
- pip package manager
- Git (optional)

### Steps

1. Clone or download the application:
   ```bash
   git clone https://github.com/yourusername/jlens.git
   cd jlens
   ```

2. Install dependencies:
   ```bash
   pip install -r dependencies.txt
   ```

3. Configure environment (optional):
   ```bash
   # Set environment variables if needed
   export STREAMLIT_SERVER_PORT=5000
   export STREAMLIT_SERVER_HEADLESS=true
   ```

4. Start the application:
   ```bash
   streamlit run app.py
   ```

5. Configure a reverse proxy (optional):
   ```nginx
   # Nginx configuration example
   server {
       listen 80;
       server_name jlens.yourdomain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

## Docker Deployment

1. Create a Dockerfile:
   ```Dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY . /app/
   
   RUN apt-get update && \
       apt-get install -y --no-install-recommends \
       build-essential \
       graphviz \
       graphviz-dev \
       && rm -rf /var/lib/apt/lists/*
   
   RUN pip install --no-cache-dir -r dependencies.txt
   
   EXPOSE 5000
   
   CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]
   ```

2. Build and run the Docker image:
   ```bash
   docker build -t jlens:latest .
   docker run -p 5000:5000 jlens:latest
   ```

3. Access the application at http://localhost:5000

## Deploying to Cloud Platforms

### Heroku

1. Create a Procfile:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Deploy to Heroku:
   ```bash
   heroku create jlens-app
   git push heroku main
   ```

### Google Cloud Run

1. Build and push a Docker image:
   ```bash
   gcloud builds submit --tag gcr.io/your-project/jlens
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy jlens --image gcr.io/your-project/jlens --platform managed
   ```

## Configuration Options

JLens application can be configured through the following parameters:

- `--server.port`: Port to run the Streamlit server on (default: 5000)
- `--server.address`: Address to bind the server to (default: 0.0.0.0)
- `--server.headless`: Run in headless mode (default: true)
- `--server.maxUploadSize`: Maximum file size for uploads in MB (default: 200)

## Post-Deployment Verification

After deployment, verify the application is working correctly:

1. Upload a sample Java project ZIP file
2. Check if analysis completes successfully
3. Verify all tabs and visualizations work as expected

## Troubleshooting

- If the application fails to start, check the logs for error messages
- If file uploads fail, check the maxUploadSize setting
- If visualizations don't render, ensure all dependencies are properly installed

## Security Considerations

- The application doesn't require authentication by default
- Consider adding authentication if deploying to a public server
- Set up HTTPS for secure connections in production environments

---

© 2025 JLens - Zensar Diamond Team