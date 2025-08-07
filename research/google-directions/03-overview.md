# Google Directions API - Overview (Legacy)

Based on: https://developers.google.com/maps/documentation/directions/overview

## Key Capabilities
- Calculate directions between locations
- Support multiple transportation modes (driving, walking, transit, bicycling)
- Return route details in JSON or XML formats

## Primary Features
Calculate routes considering:
- **Travel time** (primary factor)
- Distance
- Number of turns

## Transportation Modes
- **Driving**
- **Walking**
- **Transit**
- **Bicycling**

## Request Flexibility
Specify origins/destinations via:
- Text strings
- Place IDs
- Latitude/longitude coordinates
- Support multipart directions with waypoints

## Technical Details
- Web service API
- Returns most efficient routes
- Client libraries available in:
  - Java
  - Python
  - Go
  - Node.js

## Important Status Note
**"This product or feature is in Legacy status"** - developers should consider migration to newer services.

## Sample Request Format
```
https://maps.googleapis.com/maps/api/directions/json
  ?destination=Montreal
  &origin=Toronto
  &key=YOUR_API_KEY
```

## Recommended Next Steps
1. Set up Google Cloud project
2. Obtain API key
3. Review documentation
4. Integrate into application