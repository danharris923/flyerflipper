# Google Places API - Overview

Based on: https://developers.google.com/maps/documentation/places/web-service/overview

## Key Technical Details
- **Service Type**: Web service API for location data retrieval
- **Primary Endpoints**: 
  - `/places`
  - `places:searchText`
- **Response Format**: JSON
- **Authentication**: API key or OAuth token

## Core Capabilities

### 1. Place Search
- Text-based searches
- Nearby location queries
- Categorical searches

### 2. Data Retrieval Features
- Place details (address, contact info)
- User reviews
- Operating hours
- Photos
- Place ID lookup

## Technical Implementation Steps
1. Set up Google Cloud project
2. Obtain API key
3. Make HTTP requests to service endpoints
4. Process JSON responses

## Example Request Structure
```
https://places.googleapis.com/v1/places/PLACE_ID?fields=addressComponents&key=YOUR_API_KEY
```

## Key Platforms
- Android SDK
- iOS SDK
- JavaScript
- Web Services

## Important Version Note
**Places API (New) is the current version. Places API is now Legacy and can no longer be enabled.**

## Recommended Best Practices
- Use platform-specific Places library
- Leverage place IDs across different Google Maps Platform APIs
- Implement proper error handling
- Respect API usage limits