# CrisisFlow MVP - Current Capabilities

## What is CrisisFlow?

CrisisFlow is a **Real-Time Disaster Intelligence Platform** that helps emergency responders make faster, smarter decisions during crises. It aggregates disaster reports from multiple sources, uses AI to verify and structure the data, and visualizes everything on an interactive map.

## Current MVP Features (What Works Now)

### 1. **Report Submission** 📝
- Users can submit text reports about disasters (fires, floods, earthquakes, etc.)
- Optional image upload for visual verification
- Reports are processed in real-time

### 2. **AI-Powered Processing** 🤖
- **Text Analysis**: Extracts key information from reports:
  - Location (address/landmark)
  - Hazard type (Fire, Flood, Earthquake, Storm, Tornado)
  - Severity level (Low, Medium, High)
  - Confidence score (0-100%)
- **Image Analysis**: Uses GPT-4o or Gemini Pro Vision to:
  - Verify if images show actual disasters
  - Extract location from visible street signs
  - Estimate severity from visual evidence
  - Automatically increases confidence for image-based reports

### 3. **Smart Clustering** 🎯
- Groups similar reports within 500 meters into single "Incidents"
- Prevents duplicate pins on the map
- Increases confidence with multiple witnesses
- Example: If 12 people report a fire at the same building, it shows as "CONFIRMED INCIDENT: 12 witnesses" instead of 12 separate reports

### 4. **Real-Time Map Visualization** 🗺️
- Interactive map showing all active incidents
- **Color-coded markers**:
  - 🔴 Red = High severity
  - 🟠 Orange = Medium severity
  - 🟢 Green = Low severity
- **Real geocoding**: Converts addresses to precise coordinates
- **Danger zones**: Red circles (500m radius) around high-severity incidents
- Auto-centers on active incidents

### 5. **Live Dashboard** 📊
- Real-time updates every 5 seconds
- Report feed showing all incidents
- Confidence scores and witness counts
- Timestamp tracking

## Technical Stack

**Backend:**
- Python FastAPI
- SQLite database
- OpenAI GPT-4o / Google Gemini Pro Vision
- OpenStreetMap Nominatim (geocoding)

**Frontend:**
- Next.js 14 (React)
- Tailwind CSS (dark mode)
- Leaflet maps
- Real-time polling

## What It Can Do Right Now

✅ Accept disaster reports via text or image  
✅ Automatically extract location, hazard type, and severity  
✅ Geocode addresses to map coordinates  
✅ Cluster nearby reports into incidents  
✅ Visualize incidents on an interactive map  
✅ Show danger zones for high-severity incidents  
✅ Update in real-time (every 5 seconds)  
✅ Increase confidence with multiple witnesses  

## Example Use Case

**Scenario**: A fire breaks out at "123 Main Street, San Francisco"

1. **First Report**: "Fire at 123 Main Street!"
   - AI extracts: Location, Hazard=Fire, Severity=High
   - Geocodes to coordinates
   - Creates new Incident on map

2. **Second Report** (from nearby): "Big fire on Main St!"
   - AI processes and geocodes
   - Finds existing incident within 500m
   - **Attaches to same incident** (doesn't create duplicate)
   - Witness count: 2
   - Confidence increases

3. **Third Report** (with photo): User uploads image of fire
   - Vision model verifies it's actually a fire
   - Extracts location from street sign in image
   - High confidence score (image verified)
   - Witness count: 3
   - Map shows danger zone (red circle)

**Result**: Emergency responders see ONE confirmed incident with 3 witnesses, high confidence, and a clear danger zone on the map - not 3 separate confusing reports.

## Current Limitations (What's Not Done Yet)

❌ User authentication (anyone can submit)  
❌ WebSocket real-time (currently polling every 5s)  
❌ Resource tracking (needed vs. available supplies)  
❌ Route planning integration  
❌ Mobile app  
❌ SMS/Twitter integration for data ingestion  
❌ Historical data analysis  
❌ Multi-language support  

## Demo Access

- **Backend API**: `http://127.0.0.1:8000`
- **Frontend Dashboard**: `http://localhost:3000`
- **API Documentation**: `http://127.0.0.1:8000/docs`

---

**Status**: ✅ Fully functional MVP ready for testing and demonstration

