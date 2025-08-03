# Deployment to Render

## Your Deployment
Your app is deployed at: https://alltalk.onrender.com

## Prerequisites
1. A Render account (free tier works)
2. A GitHub repository with your code

## Environment Variables Required
Set these in your Render dashboard:
- `SECRET_KEY`: Django secret key (Render generates this automatically)
- `DATABASE_URL`: PostgreSQL connection string (auto-configured by Render)
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Your Render domain (e.g., `alltalk.onrender.com`)
- `OPENAI_API_KEY`: Your OpenAI API key for AI features
- `ALGOLIA_APPLICATION_ID`: Your Algolia app ID (optional)
- `ALGOLIA_API_KEY`: Your Algolia admin API key (optional)
- `ALGOLIA_SEARCH_API_KEY`: Your Algolia search-only API key (optional)

## Deployment Steps

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add image upload feature and fix Algolia UUID issue"
   git push origin main
   ```

2. **Automatic Deployment**:
   - Render will automatically detect the push and start deploying
   - Check progress at https://dashboard.render.com
   - Deployment takes about 5-10 minutes

## Important Notes

### Media Files Storage
⚠️ **Render's filesystem is ephemeral** - uploaded images will be lost on redeploy!

For production, you need to configure external storage for media files:

#### Option 1: Cloudinary (Recommended for free tier)
1. Sign up at https://cloudinary.com (free tier available)
2. Install: `pip install django-cloudinary-storage`
3. Add to settings.py:
```python
if not DEBUG:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
        'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

#### Option 2: AWS S3
1. Create an S3 bucket
2. Install: `pip install django-storages boto3`
3. Configure in settings.py with S3 credentials

#### Option 3: Temporary Solution
For testing only - images will be lost on each deploy:
- Current configuration stores images locally
- They will persist until the next deploy
- Suitable for demo/testing only

### Database
- Your database should already be configured and working
- The migration for DreamImage will run automatically during deployment

## Monitoring
- Check logs: https://dashboard.render.com → Your Service → Logs
- Your app: https://alltalk.onrender.com

## What Changed in This Deployment
1. Added image upload feature (up to 3 images per dream)
2. Fixed Algolia UUID serialization issue
3. Disabled automatic Algolia indexing
4. Added image optimization with Pillow
5. Created DreamImage model for storing images