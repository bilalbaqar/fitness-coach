# 🚀 Vercel Deployment Guide

## Quick Deploy to Vercel

### Step 1: Prepare Your Repository
1. Make sure all frontend files are committed to your GitHub repository
2. Ensure your frontend code is in the `frontend/` directory
3. Verify `package.json` has the correct build script

### Step 2: Deploy to Vercel
1. **Sign up/Login**: Go to [vercel.com](https://vercel.com)
2. **New Project**: Click "New Project"
3. **Import Git Repository**: Select your fitness-coach repository
4. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. **Environment Variables** (optional):
   ```
   VITE_API_URL=https://fitness-coach-production.up.railway.app
   ```

### Step 3: Deploy
1. **Click "Deploy"**
2. **Wait for build** (usually 1-2 minutes)
3. **Get your URL**: `https://your-app.vercel.app`

## 🎯 Expected Behavior

### Successful Deployment
- ✅ Build completes without errors
- ✅ App loads with proper styling (Tailwind CSS)
- ✅ API calls work to Railway backend
- ✅ No console errors

### Test Your Deployment
1. **Visit your Vercel URL**
2. **Open browser dev tools** (F12)
3. **Check Console** for any errors
4. **Test API calls** to your Railway backend

## 🔧 Configuration Files

### vercel.json
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Framework**: Vite
- **SPA Routing**: All routes redirect to index.html
- **CORS Headers**: Configured for API calls

### src/config.js
- **Environment Detection**: Automatically switches between dev/prod
- **API URL**: Points to your Railway backend in production
- **Backward Compatibility**: Maintains `window.__VITE_API__`

## 🔄 Continuous Deployment

### Automatic Deploys
- Push to `main` branch = automatic deployment
- Vercel watches your GitHub repository
- Preview deployments for pull requests

### Manual Deploys
- Use Vercel dashboard "Redeploy" button
- Deploy from specific Git commits

## 🎨 Customization

### Custom Domain
1. **Add Domain**: In Vercel dashboard → Settings → Domains
2. **Configure DNS**: Point your domain to Vercel
3. **SSL**: Automatic HTTPS

### Environment Variables
```bash
# In Vercel dashboard → Settings → Environment Variables
VITE_API_URL=https://your-backend-url.com
```

## 🔍 Troubleshooting

### Common Issues

**1. Build Fails**
- Check Vercel build logs
- Ensure all dependencies are in `package.json`
- Verify Node.js version compatibility

**2. API Calls Fail**
- Check CORS configuration
- Verify API URL in `config.js`
- Test backend endpoints directly

**3. Styling Issues**
- Ensure Tailwind CSS is properly configured
- Check `index.css` import
- Verify PostCSS configuration

**4. Routing Issues**
- Check `vercel.json` rewrites configuration
- Ensure SPA routing is set up correctly

### Debug Commands
```bash
# Local build test
npm run build

# Local preview
npm run preview

# Check build output
ls dist/
```

## 📊 Monitoring

### Vercel Dashboard
- **Analytics**: Page views, performance metrics
- **Functions**: Serverless function logs
- **Deployments**: Build history and status

### Performance
- **Core Web Vitals**: Automatic monitoring
- **Lighthouse**: Built-in performance testing
- **Edge Network**: Global CDN

## 💰 Cost Management

### Free Tier Limits
- **Bandwidth**: 100GB/month
- **Build Minutes**: 6,000 minutes/month
- **Functions**: 100GB-hours/month
- **Custom Domains**: Unlimited

### Upgrading
- **Pro Plan**: $20/month for team features
- **Enterprise**: Custom pricing

## 🎉 Success!

Once deployed, your app will be available at:
`https://your-app.vercel.app`

### Integration with Backend
Your frontend will automatically connect to:
`https://fitness-coach-production.up.railway.app`

### Next Steps
1. **Test all features** work with the deployed backend
2. **Set up custom domain** (optional)
3. **Configure analytics** (optional)
4. **Set up monitoring** (optional)

## 🔗 Useful Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Vercel CLI**: `npm i -g vercel`
- **Documentation**: https://vercel.com/docs
- **Support**: https://vercel.com/support
