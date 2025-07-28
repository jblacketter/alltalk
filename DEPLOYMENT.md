# Dream Journal Deployment Guide

## Deploying to Render

### Prerequisites
1. A [Render](https://render.com) account
2. Your Algolia API credentials
3. (Optional) OpenAI API key for AI features

### Deployment Steps

1. **Fork/Push to GitHub**
   - Ensure your code is pushed to a GitHub repository

2. **Create a New Web Service on Render**
   - Log in to Render
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

3. **Environment Variables**
   Set these in Render's dashboard:
   - `ALGOLIA_APPLICATION_ID`: Your Algolia app ID
   - `ALGOLIA_API_KEY`: Your Algolia admin API key
   - `ALGOLIA_SEARCH_API_KEY`: Your Algolia search-only API key
   - `OPENAI_API_KEY`: (Optional) Your OpenAI API key

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically:
     - Create a PostgreSQL database
     - Install dependencies
     - Run migrations
     - Initialize Algolia index
     - Start the application

5. **Post-Deployment**
   - Visit `https://your-app.onrender.com/admin`
   - Create a superuser via Render Shell:
     ```bash
     python manage.py createsuperuser
     ```

### Data Migration from Local

1. **Export local data:**
   ```bash
   ./export_data.sh
   ```

2. **In Render Shell:**
   ```bash
   # Upload fixtures directory to Render
   python manage.py loaddata fixtures/users.json
   python manage.py loaddata fixtures/dreams.json
   python manage.py loaddata fixtures/patterns.json
   python manage.py loaddata fixtures/sharing.json
   ```

### Media Storage

For production, you'll need to set up external media storage:

#### Option 1: Cloudinary (Recommended)
1. Create a [Cloudinary](https://cloudinary.com) account
2. Install: `pip install django-cloudinary-storage`
3. Add to `INSTALLED_APPS`:
   ```python
   'cloudinary_storage',
   'cloudinary',
   ```
4. Configure in settings:
   ```python
   CLOUDINARY_STORAGE = {
       'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
       'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
       'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
   }
   DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
   ```

#### Option 2: Render Disk ($7/month)
- Add a disk in Render dashboard
- Mount at `/media`
- Update `MEDIA_ROOT` in settings

### Custom Domain

1. In Render dashboard → Settings → Custom Domains
2. Add your domain
3. Update DNS records as instructed
4. Update `ALLOWED_HOSTS` environment variable

### Monitoring

- Render provides basic logs and metrics
- For advanced monitoring, consider:
  - Sentry for error tracking
  - New Relic for performance monitoring

### Troubleshooting

**Static files not loading:**
- Run `python manage.py collectstatic`
- Check WhiteNoise configuration

**Database connection errors:**
- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL addon status

**Algolia search not working:**
- Verify API keys are correct
- Run `python manage.py init_algolia_index`
- Check browser console for errors

### Backup Strategy

1. **Database:**
   - Render provides daily backups on paid plans
   - Manual backup: `pg_dump $DATABASE_URL > backup.sql`

2. **Media files:**
   - If using Cloudinary, files are already backed up
   - If using disk, set up regular backups

### Updates

To deploy updates:
1. Push changes to GitHub
2. Render will automatically rebuild and deploy
3. Migrations run automatically via `build.sh`

### Security Checklist

- [ ] Change `SECRET_KEY` from default
- [ ] Set `DEBUG=False`
- [ ] Use HTTPS (automatic on Render)
- [ ] Regular security updates
- [ ] Strong admin passwords
- [ ] Review privacy settings