# Quick Deployment Guide

## Deploy to Render in 5 Minutes

### Step 1: Prepare Repository

```bash
cd bronze_flask
git init
git add .
git commit -m "Initial Flask web app for BRONZE: 1177 BC"
```

### Step 2: Push to GitHub

```bash
# Create new repo on GitHub (https://github.com/new)
# Name it: bronze-1177-bc-web

git remote add origin https://github.com/YOUR_USERNAME/bronze-1177-bc-web.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Render

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect account"** (connect GitHub)
4. Find your repository: `bronze-1177-bc-web`
5. Click **"Connect"**

**Render will auto-detect `render.yaml` and configure:**
- Name: bronze-1177-bc
- Environment: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

6. Click **"Create Web Service"**
7. Wait 2-3 minutes
8. Your app will be live at: `https://bronze-1177-bc.onrender.com`

### Step 4: Test Your Deployment

Visit your Render URL and:
- Click "Start New Game"
- Perform a few actions (Harvest, Build, etc.)
- Verify turns advance correctly
- Test on mobile browser

---

## Alternative: Deploy Without GitHub

If you don't want to use GitHub:

1. Create a **Public Git Repository** elsewhere (GitLab, Bitbucket)
2. On Render, choose **"Public Git Repository"**
3. Paste your repository URL
4. Follow same steps as above

---

## Free Tier Limitations

- **Cold starts:** App sleeps after 15 minutes of inactivity
- **First load:** May take 30-60 seconds to wake up
- **No issue for:** Personal projects, portfolios, demos

**To eliminate cold starts:** Upgrade to paid tier ($7/month)

---

## Environment Variables (Optional)

If you want to set a custom secret key:

1. In Render Dashboard → Your Service → **Environment**
2. Click **"Add Environment Variable"**
3. Key: `SECRET_KEY`
4. Value: `your-random-secret-string-here`
5. Click **"Save Changes"**

(Render auto-generates one if you don't set it)

---

## Custom Domain (Optional)

1. In Render Dashboard → Your Service → **Settings**
2. Scroll to **"Custom Domain"**
3. Click **"Add Custom Domain"**
4. Enter: `bronze.yourdomain.com`
5. Add CNAME record to your DNS:
   - Name: `bronze`
   - Value: `bronze-1177-bc.onrender.com`
6. Wait for DNS propagation (~5 minutes)

---

## Monitoring

View logs in real-time:
1. Render Dashboard → Your Service → **Logs**
2. See all requests, errors, and server activity

---

## Updates

Push new changes:

```bash
git add .
git commit -m "Update game balance"
git push
```

Render will **auto-deploy** in ~2 minutes.

---

## Troubleshooting

**Deployment failed:**
- Check **Logs** tab in Render dashboard
- Common issues:
  - Missing `requirements.txt`
  - Python version mismatch
  - Syntax errors in `render.yaml`

**App crashes on startup:**
- Verify `gunicorn app:app` works locally:
  ```bash
  gunicorn app:app
  ```
- Check for missing imports

**Session data not persisting:**
- Ensure `SECRET_KEY` environment variable is set
- Don't change SECRET_KEY after deployment (invalidates sessions)

---

## Success Checklist

- ✅ App loads at Render URL
- ✅ "Start New Game" creates new session
- ✅ Actions update game state
- ✅ Turns advance automatically
- ✅ Victory/defeat screens work
- ✅ Mobile responsive (test on phone)

**Deployment time:** ~5 minutes
**Cost:** $0 (free tier)
