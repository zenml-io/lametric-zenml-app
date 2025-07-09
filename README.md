# ZenML LaMetric App

A FastAPI application that polls Mixpanel API and GitHub API to display ZenML metrics on LaMetric devices.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Mixpanel service account credentials
```

3. Run locally:
```bash
python main.py
```

## Deployment to Fly.io

1. Initialize fly app:
```bash
fly launch
```

2. Set environment variables:
```bash
fly secrets set MIXPANEL_PROJECT_ID=your_project_id
fly secrets set MIXPANEL_SERVICE_ACCOUNT_USERNAME=your_service_account_username
fly secrets set MIXPANEL_SERVICE_ACCOUNT_SECRET=your_service_account_secret
fly secrets set GITHUB_TOKEN=your_github_token  # Optional - for higher rate limits
```

3. Deploy:
```bash
fly deploy
```

## LaMetric Configuration

Configure your LaMetric device to poll the `/metrics` endpoint:
- URL: `https://your-app.fly.dev/metrics`
- Poll interval: 30 seconds (or as desired)

## API Endpoints

- `GET /`: Health check
- `GET /metrics`: LaMetric-formatted metrics endpoint