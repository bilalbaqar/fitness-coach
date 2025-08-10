# 🚀 Railway Deployment Guide

## Quick Deploy to Railway

### Step 1: Prepare Your Repository
1. Make sure all files are committed to your GitHub repository
2. Ensure your backend code is in the `backend/` directory

### Step 2: Deploy to Railway
1. **Sign up/Login**: Go to [railway.app](https://railway.app)
2. **New Project**: Click "New Project"
3. **Deploy from GitHub**: Select "Deploy from GitHub repo"
4. **Select Repository**: Choose your fitness-coach repository
5. **Configure**: Railway will auto-detect it's a Python project

### Step 3: Add PostgreSQL Database
1. **Add Service**: In your Railway project, click "New Service"
2. **Database**: Select "Database" → "PostgreSQL"
3. **Connect**: Railway will automatically link the database to your app

### Step 4: Configure Environment Variables
In your Railway project dashboard, go to "Variables" and add:

```bash
# Database (Railway will auto-set this)
DATABASE_URL=postgresql://...

# Authentication
JWT_SECRET=your-super-secure-secret-key-here
AGENT_TOKEN=your-agent-token-for-tools

# CORS (update with your frontend URL)
FRONTEND_ORIGIN=https://your-frontend-domain.com

# ElevenLabs (optional)
ELEVENLABS_API_KEY=your-elevenlabs-key
```

### Step 5: Deploy
1. **Automatic**: Railway will auto-deploy when you push to GitHub
2. **Manual**: Click "Deploy" in Railway dashboard
3. **Monitor**: Watch the deployment logs

## 🎯 Expected Behavior

### Successful Deployment
- ✅ Build completes without errors
- ✅ Database tables are created
- ✅ Demo data is seeded
- ✅ Health check passes
- ✅ API endpoints are accessible

### Test Your Deployment
```bash
# Health check
curl https://your-app.railway.app/

# Test API endpoints
curl https://your-app.railway.app/api/me
curl https://your-app.railway.app/api/goals
curl https://your-app.railway.app/api/readiness/today
```

## 🔧 Troubleshooting

### Common Issues

**1. Build Fails**
- Check Railway logs for Python version issues
- Ensure all dependencies are in `requirements.txt`
- Verify `Procfile` syntax

**2. Database Connection Fails**
- Ensure PostgreSQL service is added
- Check `DATABASE_URL` environment variable
- Verify `psycopg2-binary` is in requirements

**3. Import Errors**
- Check file paths and imports
- Ensure all Python files are in the correct directory
- Verify `__init__.py` files exist if needed

**4. CORS Issues**
- Update `FRONTEND_ORIGIN` environment variable
- Check CORS configuration in `main.py`

### Debug Commands
```bash
# Check Railway logs
railway logs

# SSH into Railway container
railway shell

# Check environment variables
railway variables
```

## 📊 Monitoring

### Railway Dashboard
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history and status

### Health Checks
- Railway automatically checks `/` endpoint
- Returns `{"ok": True, "service": "ai-sports-coach-backend"}`

## 🔄 Continuous Deployment

### Automatic Deploys
- Push to `main` branch = automatic deployment
- Railway watches your GitHub repository
- No manual intervention needed

### Manual Deploys
- Use Railway dashboard "Deploy" button
- Useful for testing or rollbacks

## 💰 Cost Management

### Free Tier Limits
- **Hours**: 500 hours/month
- **Storage**: 1GB
- **Bandwidth**: 100GB/month

### Upgrading
- **Pro Plan**: $5/month for unlimited hours
- **Team Plan**: $20/month for team features

## 🎉 Success!

Once deployed, your API will be available at:
`https://your-app-name.railway.app`

### API Documentation
- **Swagger UI**: `https://your-app-name.railway.app/docs`
- **ReDoc**: `https://your-app-name.railway.app/redoc`

### Frontend Integration
Update your frontend to use the Railway URL:
```javascript
const API_BASE = 'https://your-app-name.railway.app';
```
