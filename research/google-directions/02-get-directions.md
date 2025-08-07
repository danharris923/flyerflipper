# Google Directions API - Get Directions

Based on: https://developers.google.com/maps/documentation/directions/get-directions

## Key Features
- Calculate routes between origins and destinations
- Support multiple transportation modes (driving, walking, bicycling, transit)
- Specify waypoints and route preferences
- Return detailed route information including distance, duration, and step-by-step directions

## Required Parameters
- **origin**: Starting point (address, place ID, or coordinates)
- **destination**: Endpoint (address, place ID, or coordinates)

## Optional Parameters
- **mode**: Transportation type (default is driving)
- **waypoints**: Intermediate locations
- **avoid**: Route restrictions (tolls, highways, ferries)
- **alternatives**: Generate multiple route options
- **departure_time**: Specify travel timing
- **units**: Choose metric or imperial measurements

## Request Format
```
https://maps.googleapis.com/maps/api/directions/outputFormat?parameters
```

## Response Includes
- Route legs
- Total distance and duration
- Turn-by-turn instructions
- Polyline encoding of route
- Geocoded waypoint information

## Best Practices
- Prefer place IDs over addresses
- Use region parameter for location disambiguation
- Be aware of URL length limitations (16,384 characters)