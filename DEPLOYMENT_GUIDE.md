# 🚀 Streamlit Cloud Deployment Guide

# =====================================

## Complete Step-by-Step Guide to Deploy Your OIC ADEI Analytics App

---

## 📋 Prerequisites

Before you start, make sure you have:

- ✅ GitHub account
- ✅ Streamlit Cloud account (free at [share.streamlit.io](https://share.streamlit.io))
- ✅ Your database credentials ready (Neon PostgreSQL)
- ✅ Clean, working local version of the app

---

## 🎯 Step 1: Prepare Your Repository

### 1.1 Initialize Git Repository

```bash
cd /Users/mac/Documents/My_ML_Project/oic-2021-2025

# Initialize git (if not already done)
git init

# Check what will be committed
git status
```

### 1.2 Review Files to Commit

Make sure these essential files are present:

```
✅ streamlit_app.py
✅ country_comparison.py
✅ geographic_analysis.py
✅ rag_search.py
✅ config.py
✅ requirements.txt
✅ .gitignore
✅ .env.example
✅ README.md or README_DEPLOYMENT.md
✅ .streamlit/secrets.toml.example
```

Files that should NOT be committed (check .gitignore):

```
❌ .env (contains real credentials)
❌ __pycache__/
❌ .venv/
❌ streamlit_env/
❌ *.db
❌ *.xlsx
❌ OIC ADEI Data 2021-2025.xlsx
```

### 1.3 Test Locally One More Time

```bash
# Make sure app runs without errors
streamlit run streamlit_app.py

# Open http://localhost:8501 and verify all tabs work
```

---

## 🐙 Step 2: Push to GitHub

### 2.1 Create GitHub Repository

1. Go to [github.com](https://github.com)
2. Click **"New repository"** (green button)
3. Repository name: `oic-adei-analytics` (or your choice)
4. Description: "OIC ADEI Analytics Dashboard - Streamlit App"
5. Choose **Public** or **Private**
6. **DON'T** initialize with README (we already have one)
7. Click **"Create repository"**

### 2.2 Add Files and Push

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: OIC ADEI Analytics Streamlit App"

# Add GitHub remote (replace with your username)
git remote add origin https://github.com/YOUR_USERNAME/oic-adei-analytics.git

# Set default branch
git branch -M main

# Push to GitHub
git push -u origin main
```

### 2.3 Verify on GitHub

1. Go to your repository URL
2. Check that all files are there
3. **IMPORTANT**: Verify `.env` is NOT visible (should be blocked by .gitignore)

---

## ☁️ Step 3: Deploy on Streamlit Cloud

### 3.1 Sign Up / Log In

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in"**
3. Choose **"Sign in with GitHub"**
4. Authorize Streamlit to access your repositories

### 3.2 Create New App

1. Click **"New app"** button
2. Fill in the form:
   - **Repository**: Select `YOUR_USERNAME/oic-adei-analytics`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **App URL**: Choose a unique name (e.g., `oic-adei-analytics`)

### 3.3 Configure Secrets

**CRITICAL STEP!** Your app needs database credentials.

1. Click **"Advanced settings"** (before deploying)
2. In the **"Secrets"** section, paste this configuration:

```toml
[database]
host = "ep-noisy-darkness-adflnyur-pooler.c-2.us-east-1.aws.neon.tech"
port = 5432
database = "neondb"
user = "neondb_owner"
password = "npg_mvnKs8P2Vrbd"
sslmode = "require"
```

**Note**: If you have different credentials, use those instead!

3. Optional: Add OpenAI key if you want enhanced RAG:

```toml
[openai]
api_key = "sk-your-openai-key-here"
```

### 3.4 Deploy!

1. Click **"Deploy!"** button
2. Wait 2-5 minutes while Streamlit Cloud:
   - ✅ Clones your repository
   - ✅ Installs dependencies from requirements.txt
   - ✅ Starts your app
   - ✅ Makes it publicly accessible

### 3.5 Monitor Deployment

Watch the logs in real-time:

- ✅ Green messages = Good
- ⚠️ Yellow warnings = Usually OK (like LangChain deprecation warnings)
- ❌ Red errors = Need to fix

Common warnings you can ignore:

```
LangChainDeprecationWarning: Importing HuggingFaceEmbeddings...
TensorFlow binary is optimized to use available CPU instructions...
```

---

## 🎉 Step 4: Verify Deployment

### 4.1 Access Your App

Once deployed, you'll get a URL like:

```
https://oic-adei-analytics.streamlit.app
```

### 4.2 Test All Features

Go through each tab and verify:

- ✅ **Executive Dashboard** - Charts load correctly
- ✅ **Pillar Analysis** - Radar charts and heatmaps work
- ✅ **Country Comparison** - Can select and compare countries
- ✅ **Geographic Analysis** - World map renders
- ✅ **RAG Search** - Search functionality works (may take 30s on first load)
- ✅ **Trends Analysis** - Time series charts display

### 4.3 Check for Errors

If you see errors:

1. Check the **Manage app** → **Logs** section
2. Look for red error messages
3. Common issues and fixes below

---

## 🐛 Troubleshooting

### Issue 1: "ModuleNotFoundError"

**Error**: `ModuleNotFoundError: No module named 'psycopg2'`

**Fix**: Update `requirements.txt` to use `psycopg2-binary`:

```bash
# Change in requirements.txt:
psycopg2-binary==2.9.9  # Instead of just psycopg2
```

Then commit and push:

```bash
git add requirements.txt
git commit -m "Fix: Use psycopg2-binary for Streamlit Cloud"
git push
```

Streamlit Cloud will auto-redeploy.

---

### Issue 2: Database Connection Failed

**Error**: `could not connect to server` or `connection refused`

**Fix**:

1. Go to **App settings** → **Secrets**
2. Verify credentials are correct
3. Make sure your database (Neon) allows connections from Streamlit Cloud IPs
4. Check that `sslmode = "require"` is set

---

### Issue 3: App is Slow or Times Out

**Symptoms**: App takes forever to load or shows "App is sleeping"

**Fix**:

- Streamlit Cloud free tier apps sleep after inactivity
- First load after sleep takes 30-60 seconds (normal)
- Optimize queries in `config.py` to use smaller cache times
- Consider upgrading to Streamlit Cloud Pro for always-on apps

---

### Issue 4: Secrets Not Loading

**Error**: `KeyError: 'database'` or similar

**Fix**: Check that secrets are in correct TOML format:

```toml
[database]  # Section header REQUIRED
host = "..."  # Use quotes
port = 5432   # Numbers without quotes
```

Update secrets: **Manage app** → **Settings** → **Secrets** → Edit

---

### Issue 5: Excel File Missing Error

**Error**: `FileNotFoundError: OIC ADEI Data 2021-2025.xlsx`

**Fix**: The app should use database, not Excel file. Check that:

1. `.gitignore` excludes `*.xlsx`
2. App uses `load_data()` function that connects to database
3. No hardcoded paths to Excel files in your code

---

## 🔄 Updating Your Deployed App

### Making Changes

1. **Edit locally and test**

```bash
streamlit run streamlit_app.py
```

2. **Commit and push**

```bash
git add .
git commit -m "Description of changes"
git push
```

3. **Auto-redeploy**
   - Streamlit Cloud detects the push
   - Automatically redeploys your app
   - Wait 1-2 minutes for changes to appear

### Updating Secrets

1. Go to **Manage app** → **Settings** → **Secrets**
2. Edit the TOML configuration
3. Click **Save**
4. App will restart automatically

---

## 🔒 Security Best Practices

### ✅ DO:

- Use `.gitignore` to exclude `.env` file
- Store credentials in Streamlit Cloud Secrets
- Use SSL for database connections (`sslmode = "require"`)
- Keep dependencies updated

### ❌ DON'T:

- Never commit `.env` file to GitHub
- Don't hardcode passwords in code
- Don't share your secrets.toml publicly
- Don't commit database files or Excel files with sensitive data

---

## 📊 Monitoring Your App

### Analytics

Streamlit Cloud provides:

- **Views**: Number of app loads
- **Users**: Unique visitors
- **Errors**: Runtime errors
- **Logs**: Real-time application logs

Access via: **Manage app** → **Analytics**

### Resource Usage

Free tier limits:

- 1 GB RAM
- 1 CPU core
- Unlimited users (with rate limits)
- Apps sleep after 7 days inactivity

If you exceed limits, consider upgrading or optimizing:

- Reduce RAG search memory usage
- Cache more aggressively
- Limit concurrent users

---

## 🎓 Useful Commands

### Local Development

```bash
# Run app locally
streamlit run streamlit_app.py

# Run on specific port
streamlit run streamlit_app.py --server.port 8502

# Clear cache
streamlit cache clear
```

### Git Commands

```bash
# Check status
git status

# Stage changes
git add .

# Commit
git commit -m "Your message"

# Push to GitHub
git push

# Pull latest changes
git pull

# View commit history
git log --oneline
```

### Viewing Logs

```bash
# In Streamlit Cloud: Manage app → Logs
# Or tail logs in terminal (if self-hosted)
tail -f logs/streamlit.log
```

---

## 🚀 Next Steps

### After Successful Deployment:

1. **Share your app!** Copy the URL and share with stakeholders
2. **Monitor usage** via Streamlit Cloud analytics
3. **Gather feedback** and iterate on features
4. **Add custom domain** (Pro tier only)
5. **Set up authentication** if needed (Pro tier only)

### Optional Enhancements:

- Add Google Analytics
- Implement user authentication
- Create API endpoints
- Add data export features
- Build custom themes

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Forum](https://discuss.streamlit.io)
- [GitHub Docs](https://docs.github.com)
- [Neon Database Docs](https://neon.tech/docs)

---

## 🎉 Congratulations!

Your OIC ADEI Analytics app is now live on Streamlit Cloud! 🚀

**Your app URL**: `https://your-app-name.streamlit.app`

Share it, monitor it, and iterate based on user feedback!

---

## 💬 Need Help?

If you encounter issues not covered here:

1. Check Streamlit Cloud logs for error details
2. Search [Streamlit Forum](https://discuss.streamlit.io)
3. Review [Streamlit Community Cloud FAQs](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/faq)
4. Open an issue on your GitHub repository
5. Contact Streamlit support (Pro users)

Good luck! 🍀
