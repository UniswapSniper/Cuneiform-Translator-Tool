# Render Deployment with Chrome Browser - Updated Guide

## 🎯 Overview

This guide covers deploying the Cuneiform Translator backend to Render with **Google Chrome browser support** using Docker. The Docker approach solves two key issues:
1. Python 3.13 compatibility (distutils removal)
2. Chrome browser installation on Render servers

## 📋 What Changed

### Files Modified/Created:
- ✅ `Dockerfile` - Docker container with Chrome + ChromeDriver
- ✅ `.dockerignore` - Optimized Docker build
- ✅ `render.yaml` - Updated to use Docker runtime
- ✅ `backend/requirements.txt` - Added Selenium
- ✅ `backend/utils/browser.py` - Browser automation utilities
- ✅ `backend/app/api/browser.py` - Browser test endpoints

## 🚀 Quick Deploy Steps

### 1. Push Changes to GitHub

```bash
cd /Users/jeffgoldner/Documents/CuniformTranslator

# Check status
git status

# Add all new files
git add .

# Commit changes
git commit -m "Add Docker deployment with Chrome browser support"

# Push to GitHub
git push origin main
```

### 2. Update Render Service Settings

Since we switched from Python runtime to Docker, you need to update your Render service:

**Option A: Via Render Dashboard (Recommended)**
1. Go to https://dashboard.render.com/web/srv-d5ostsngi27c73fmh750/settings
2. Scroll to "Build & Deploy"
3. Change **Runtime** from "Python" to "Docker"
4. The `render.yaml` will automatically configure the rest
5. Click "Save Changes"

**Option B: Delete and Recreate Service**
1. Delete the existing `cuneiform-api` service
2. Create new Web Service from GitHub repo
3. Render will detect `render.yaml` and use Docker automatically
4. Keep the same PostgreSQL database connection

### 3. Deploy

- Render will auto-deploy when you push to `main`
- Or manually trigger: Dashboard → "Manual Deploy" → "Deploy latest commit"
- Build time: ~5-8 minutes (Docker builds are slower than Python)

### 4. Verify Deployment

Once deployed (Status: "Live"), test the browser functionality:

```bash
# Test browser status
curl https://cuneiform-api.onrender.com/api/browser/status

# Expected response:
# {
#   "chrome_installed": true,
#   "chromedriver_installed": true,
#   "selenium_installed": true,
#   "chrome_version": "Google Chrome 131.x.x.x",
#   "chromedriver_version": "ChromeDriver 131.x.x.x",
#   ...
# }

# Test browser functionality
curl https://cuneiform-api.onrender.com/api/browser/test

# Expected response:
# {
#   "success": true,
#   "title": "Google",
#   "message": "Browser test successful",
#   ...
# }
```

## 🔧 How to Use Chrome in Your Code

### Example: Web Scraping

```python
from utils.browser import create_chrome_driver

def scrape_cuneiform_resource(url):
    """Example function using Chrome browser."""
    driver = create_chrome_driver(headless=True)
    
    try:
        driver.get(url)
        page_title = driver.title
        page_content = driver.page_source
        
        # Do your scraping/processing here
        
        return {
            'title': page_title,
            'content': page_content
        }
    finally:
        driver.quit()  # Always close the browser
```

### Example: Screenshot Capture

```python
from utils.browser import create_chrome_driver

def capture_tablet_image(url):
    """Capture screenshot of cuneiform tablet."""
    driver = create_chrome_driver(headless=True)
    
    try:
        driver.get(url)
        driver.save_screenshot('/tmp/tablet.png')
        
        with open('/tmp/tablet.png', 'rb') as f:
            image_data = f.read()
        
        return image_data
    finally:
        driver.quit()
```

## 📊 Monitoring

### View Logs
```bash
# Via dashboard
https://dashboard.render.com/web/srv-d5ostsngi27c73fmh750/logs

# Look for startup messages like:
# "Chrome version: ..."
# "ChromeDriver version: ..."
```

### Common Issues

| Issue | Solution |
|-------|----------|
| **Build fails: "Docker not enabled"** | Change Runtime to "Docker" in Render settings |
| **Chrome crashes: "no sandbox"** | Already configured in `utils/browser.py` with `--no-sandbox` |
| **Memory issues** | Upgrade Render instance type (Docker + Chrome needs more RAM) |
| **Slow builds** | Normal - Docker builds cache layers, subsequent builds are faster |

## 💰 Cost Implications

Docker deployments on Render:
- **Free tier**: 750 hours/month (same as Python)
- **Starter ($7/month)**: Recommended for Chrome (more RAM)
- **Standard ($25/month)**: Better for production with heavy browser usage

Chrome browser requires more memory:
- Minimum: 512 MB RAM
- Recommended: 1 GB+ RAM
- Free tier might struggle with headless Chrome

## 🔄 Rollback Plan

If something goes wrong, you can rollback:

```bash
# Revert to Python runtime (remove Docker)
git revert HEAD
git push origin main
```

Or use Render's dashboard:
1. Go to Deployments tab
2. Find a working previous deployment
3. Click "Redeploy"

## 🧪 Local Testing (Optional)

Test the Docker container locally before deploying:

```bash
# Build Docker image locally
cd /Users/jeffgoldner/Documents/CuniformTranslator
docker build -t cuneiform-api .

# Run locally
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e FLASK_ENV=development \
  -e DATABASE_URL=sqlite:///local.db \
  cuneiform-api

# Test in another terminal
curl http://localhost:8080/api/browser/status
curl http://localhost:8080/api/browser/test
```

## 📚 Additional Resources

- **Selenium Docs**: https://selenium-python.readthedocs.io/
- **Render Docker Docs**: https://render.com/docs/docker
- **Chrome Headless**: https://developer.chrome.com/docs/chromium/new-headless

## ✅ Next Steps After Deployment

1. [ ] Verify browser endpoints work (`/api/browser/status` and `/api/browser/test`)
2. [ ] Integrate browser automation into your cuneiform translation pipeline
3. [ ] Monitor memory usage and upgrade instance if needed
4. [ ] Set up error alerts for browser crashes
5. [ ] Consider implementing browser session pooling for better performance

---

**Last Updated**: 2026-01-22  
**Deployment Type**: Docker with Chrome + Selenium  
**Python Version**: 3.11 (in Docker container)  
**Chrome Version**: Latest stable (auto-updated in Dockerfile)
