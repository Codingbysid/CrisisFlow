# Geocoding Upgrade Notes

## Database Migration

Since we added `latitude` and `longitude` columns to the Report model, you may need to recreate your database or run a migration.

### Option 1: Delete and Recreate (Development)
```bash
# Delete the existing database
rm backend/crisisflow.db

# Restart the server - it will recreate the database with new schema
python backend/main.py
```

### Option 2: Manual Migration (Production)
If you have existing data, you'll need to:
1. Add the columns manually using SQLite
2. Or use Alembic for proper migrations (recommended for production)

## New Dependencies

Install the new geocoding dependency:
```bash
cd backend
pip install geopy==2.4.1
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

## How It Works

1. When a report is submitted, the AI processor extracts the location string
2. The location is then geocoded using OpenStreetMap Nominatim (free, no API key needed)
3. Latitude and longitude are stored in the database
4. The frontend map uses these real coordinates instead of mock data

## Rate Limiting

Nominatim has a usage policy: **1 request per second**. The geocoder includes a 1-second delay to respect this limit. For higher volume, consider:
- Using a paid geocoding service (Google Maps, Mapbox)
- Implementing caching for common locations
- Using a dedicated Nominatim server

## Fallback Behavior

If geocoding fails (invalid address, service unavailable), the report is still saved but with `latitude` and `longitude` set to `None`. The frontend will fall back to mock coordinates near San Francisco for visualization.

