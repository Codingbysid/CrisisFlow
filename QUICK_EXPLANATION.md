# CrisisFlow - Quick Explanation for Friends

## What It Does (30-Second Pitch)

**CrisisFlow is like Waze for disasters.** It takes messy reports from citizens (text, photos), uses AI to figure out what's real and where it is, groups duplicate reports together, and shows everything on a map so emergency responders know exactly what's happening and where to go.

## The Problem It Solves

When a disaster happens, emergency responders get flooded with:
- 50 people reporting the same fire (looks like 50 different fires on a map)
- Unverified reports (could be false alarms)
- No clear picture of what's actually happening

**CrisisFlow fixes this** by using AI to verify reports, group duplicates, and show one clear incident with "12 witnesses confirmed" instead of 12 confusing separate reports.

## How It Works

1. **Someone reports a disaster** (text or photo)
2. **AI processes it**: Extracts location, type (fire/flood), severity
3. **Geocodes the location**: Converts "123 Main St" to exact coordinates
4. **Checks for duplicates**: If another report is within 500m, groups them together
5. **Shows on map**: Color-coded by severity, with danger zones
6. **Updates in real-time**: Every 5 seconds

## Cool Features

- **Image Verification**: Upload a photo, AI verifies it's actually a disaster
- **Smart Clustering**: 12 reports of the same fire = 1 confirmed incident with 12 witnesses
- **Danger Zones**: Red circles on map show areas to avoid
- **Real-Time**: Map updates automatically

## What's Built vs. What's Next

### ✅ Built (MVP Complete)
- Report submission (text + images)
- AI processing (location, type, severity)
- Geocoding (address → coordinates)
- Clustering (groups nearby reports)
- Real-time map with danger zones
- Live dashboard

### 🚧 Next Steps (Future Work)
- User accounts/login
- Twitter/SMS integration (auto-ingest reports)
- Resource tracking (needed vs. available supplies)
- Route planning (avoid danger zones)
- Mobile app
- WebSocket real-time (instead of polling)

## Tech Stack (For Technical Friends)

- **Backend**: Python FastAPI
- **Frontend**: Next.js (React)
- **AI**: OpenAI GPT-4o, Google Gemini Pro Vision
- **Maps**: Leaflet
- **Geocoding**: OpenStreetMap Nominatim
- **Database**: SQLite (dev)

## Demo It

1. Submit a report: "Fire at 123 Main Street, San Francisco"
2. Watch AI extract location and geocode it
3. Submit another nearby report: "Big fire on Main St!"
4. See them cluster into one incident
5. Upload a fire photo
6. Watch confidence increase and danger zone appear

## Why It Matters

**For Responders**: Faster decisions, better resource allocation, safer routes  
**For Citizens**: Verified information, easy reporting, real-time updates  
**For Society**: Better disaster response, reduced false alarms, saved lives

---

**TL;DR**: AI-powered disaster intelligence platform that verifies reports, groups duplicates, and shows everything on a real-time map. Like Google Maps + AI verification for emergencies.

