# Google Places API - Place Details

Based on: https://developers.google.com/maps/documentation/places/web-service/details

## Key Components

### 1. Request Endpoint
- **Base URL**: `https://maps.googleapis.com/maps/api/place/details/_output_`
- Supports JSON and XML output formats
- Requires a `place_id` parameter

### 2. Required Parameters
- **place_id**: Unique identifier for a specific place
- **API key**

### 3. Optional Parameters
- **fields**: Specify desired place data types
- **language**: Set response language
- **reviews_sort**: Sort reviews by "most_relevant" or "newest"
- **sessiontoken**: Track autocomplete billing sessions

### 4. Response Categories
- **Basic Fields**: Address, name, geometry
- **Contact Fields**: Phone number, website
- **Atmosphere Fields**: Ratings, reviews, dining details

### 5. Response Structure
- `html_attributions`
- `result`: Detailed place information
- `status`: Request outcome (OK, ZERO_RESULTS, etc.)

### 6. Notable Features
- Returns up to 10 photos per place
- Provides detailed business information
- Supports multilingual responses
- Includes user reviews and ratings

## Billing Note
Fields are categorized into billing tiers (Basic, Contact, Atmosphere) with different pricing levels.

## Recommended Use
Server-side applications with proper API key management and session tracking.