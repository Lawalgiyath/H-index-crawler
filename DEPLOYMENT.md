# Deployment Guide - Scholar Metrics Scraper

This guide covers multiple deployment options for the University of Lagos Google Scholar Metrics Intelligence Portal.

## 📋 Pre-Deployment Checklist

- [x] All dependencies installed (see requirements.txt)
- [x] Test sample JSON file created
- [x] Application tested locally
- [x] Deployment files prepared (Dockerfile, Procfile, requirements.txt)

## 🏠 Local Deployment (Development)

### Windows

**Option 1: Using Batch File**
```cmd
start_app.bat
```

**Option 2: Manual**
```cmd
python Crawlee.py
```

Then open: http://localhost:5000

### Linux/Mac

```bash
python3 Crawlee.py
```

Then open: http://localhost:5000

---

## ☁️ Cloud Deployment Options

### 1. Render (Recommended - Free Tier Available)

**Steps:**

1. Create a free account at [Render.com](https://render.com)

2. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

3. In Render Dashboard:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: unilag-scholar-metrics
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn Crawlee:app`
     - **Instance Type**: Free

4. Click "Create Web Service"

5. Your app will be available at: `https://unilag-scholar-metrics.onrender.com`

---

### 2. PythonAnywhere (Easy - Free Tier)

**Steps:**

1. Create account at [PythonAnywhere.com](https://www.pythonanywhere.com)

2. Go to "Files" tab and upload:
   - Crawlee.py
   - requirements.txt
   - test_sample.json

3. Open a Bash console and run:
```bash
pip3.10 install --user flask beautifulsoup4 pandas requests python-docx
```

4. Go to "Web" tab → "Add a new web app"
   - Choose "Flask"
   - Python version: 3.10
   - Path: /home/yourusername/Crawlee.py

5. Edit WSGI configuration file:
```python
import sys
path = '/home/yourusername'
if path not in sys.path:
    sys.path.append(path)

from Crawlee import app as application
```

6. Reload web app

7. Access at: `https://yourusername.pythonanywhere.com`

---

### 3. Railway.app (Modern - Free Tier)

**Steps:**

1. Create account at [Railway.app](https://railway.app)

2. Install Railway CLI:
```bash
npm install -g @railway/cli
```

3. Login and deploy:
```bash
railway login
railway init
railway up
```

4. Configure start command in Railway dashboard:
```
gunicorn Crawlee:app --bind 0.0.0.0:$PORT
```

5. Your app will be deployed automatically

---

### 4. Heroku (Classic - Paid)

**Steps:**

1. Install Heroku CLI from [heroku.com](https://heroku.com)

2. Login and create app:
```bash
heroku login
heroku create unilag-scholar-metrics
```

3. Deploy:
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

4. Open app:
```bash
heroku open
```

5. View logs:
```bash
heroku logs --tail
```

---

### 5. Google Cloud Run (Scalable - Pay-as-you-go)

**Steps:**

1. Install Google Cloud SDK

2. Build and deploy:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/scholar-scraper
gcloud run deploy scholar-scraper \
  --image gcr.io/YOUR_PROJECT_ID/scholar-scraper \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

### 6. Docker Deployment (Self-Hosted)

**Build and run locally:**
```bash
docker build -t scholar-scraper .
docker run -p 5000:5000 scholar-scraper
```

**Using Docker Compose:**
```bash
docker-compose up -d
```

**Push to Docker Hub:**
```bash
docker tag scholar-scraper your-username/scholar-scraper
docker push your-username/scholar-scraper
```

---

### 7. AWS Elastic Beanstalk

**Steps:**

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize and deploy:
```bash
eb init -p python-3.11 scholar-scraper
eb create scholar-scraper-env
eb open
```

3. Update:
```bash
eb deploy
```

---

## 🔐 Security Considerations

### Environment Variables

For production, consider adding:

```python
# In Crawlee.py
import os

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.getenv('DEBUG', 'False') == 'True'

app.config['SECRET_KEY'] = SECRET_KEY
app.run(debug=DEBUG)
```

### Rate Limiting

Add Flask-Limiter for API protection:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per day", "10 per hour"]
)

@app.route('/crawl', methods=['POST'])
@limiter.limit("5 per hour")
def crawl():
    # existing code
```

### HTTPS

Most cloud providers offer free SSL certificates:
- Render: Automatic HTTPS
- PythonAnywhere: Free HTTPS on custom domains
- Heroku: Automatic HTTPS
- Railway: Automatic HTTPS

---

## 🧪 Testing Deployment

After deployment, test with:

```bash
# Test homepage
curl https://your-app-url.com

# Test with file upload (from local machine)
curl -X POST -F "file=@test_sample.json" https://your-app-url.com/crawl
```

---

## 📊 Monitoring & Logs

### View Logs

**Render:**
```bash
# View in dashboard or use CLI
render logs -a your-app-name
```

**Heroku:**
```bash
heroku logs --tail
```

**Railway:**
```bash
railway logs
```

**PythonAnywhere:**
- View in "Web" tab → "Log files"

---

## 🔄 Continuous Deployment

### GitHub Actions (Automatic Deploy on Push)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          curl -X POST https://api.render.com/deploy/YOUR_SERVICE_ID
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| Render | Yes (750hrs/month) | $7+/month | Small projects |
| PythonAnywhere | Yes (limited) | $5+/month | Learning/testing |
| Railway | $5 credit/month | Pay-as-you-go | Modern apps |
| Heroku | No (paid only) | $7+/month | Enterprise |
| Google Cloud Run | Yes (generous) | Pay-per-use | Scalable apps |
| Self-hosted Docker | Free | Hosting costs | Full control |

---

## 🆘 Troubleshooting

### Common Issues

**Problem**: App won't start
```bash
# Check logs for errors
# Verify all dependencies in requirements.txt
# Ensure Python version matches (3.8+)
```

**Problem**: "Module not found" errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Problem**: Port already in use
```python
# In Crawlee.py, change port
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Use different port
```

**Problem**: Timeout on scraping
```python
# Increase timeout in requests.get()
response = requests.get(url, headers=HEADERS, timeout=30)
```

---

## 📝 Post-Deployment Tasks

1. **Test thoroughly** with real data
2. **Monitor performance** and logs
3. **Set up backups** for CSV exports
4. **Configure custom domain** (optional)
5. **Add analytics** (optional)
6. **Implement authentication** if needed

---

## 🎓 Recommended for University of Lagos

**For testing/demo**: PythonAnywhere (free, easy)
**For production**: Render or Railway (reliable, auto-SSL, good free tier)
**For institutional hosting**: Self-hosted Docker on university servers

---

## 📞 Support

For deployment issues:
1. Check platform-specific documentation
2. Review application logs
3. Test locally first
4. Verify all environment variables
5. Ensure network connectivity to Google Scholar

---

**Last Updated**: September 30, 2026
**Maintained by**: University of Lagos IT Department
