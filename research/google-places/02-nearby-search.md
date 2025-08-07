# Google Places API - Nearby Search

Based on: https://developers.google.com/maps/documentation/places/web-service/nearby-search

## API Overview
- **Endpoint**: `https://places.googleapis.com/v1/places:searchNearby`
- **Method**: POST request only
- **Purpose**: Returns a list of matching places within the specified area

## Key Request Parameters

### Required Parameters
- **FieldMask**: Specifies which place data fields to return
- **locationRestriction**: Defines search area (circle with center point and radius)

### Optional Parameters
- **includedTypes/excludedTypes**: Filter by place types
- **languageCode**: Specify response language
- **maxResultCount**: Limit results (1-20, default 20)
- **rankPreference**: Sort by "POPULARITY" or "DISTANCE"

## Example Request

```bash
curl -X POST -d '{
  "includedTypes": ["restaurant"],
  "maxResultCount": 10,
  "locationRestriction": {
    "circle": {
      "center": {
        "latitude": 37.7937,
        "longitude": -122.3965
      },
      "radius": 500.0
    }
  }
}' \
-H 'Content-Type: application/json' \
-H "X-Goog-Api-Key: API_KEY" \
-H "X-Goog-FieldMask: places.displayName" \
https://places.googleapis.com/v1/places:searchNearby
```

## Response Structure
- JSON object with "places" array
- Each place contains specified fields from FieldMask
- Supports multiple data retrieval tiers with different billing SKUs

## Best Practices
- Use field masking to minimize unnecessary data retrieval
- Specify precise location and search parameters
- Choose appropriate type and primary type filters