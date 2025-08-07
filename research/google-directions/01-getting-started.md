# Google Directions API - Getting Started

Based on: https://developers.google.com/maps/documentation/directions/start

## Setup Steps
1. Create a Google Cloud project
2. Enable billing
3. Enable the Directions API
4. Create an API key

## Basic Usage Example
- Get directions between two locations using an HTTP request
- **Sample request**: 
  ```
  https://maps.googleapis.com/maps/api/directions/json?origin=Disneyland&destination=Universal+Studios+Hollywood&key=YOUR_API_KEY
  ```
- Returns JSON with route details like distance, duration, and route overview

## Key Authentication
- **API key is required** for authentication
- "The API key is a unique identifier that authenticates requests"
- **Recommended**: Restrict API key before production use

## Client Libraries
- Available for **Java, Python, Go, and Node.js**
- Provide "simple, native implementations of common tasks"

## Pricing
- Offers a **$0.00 trial** for 90 days or $300 in credits
- Running the demo does not exceed monthly quota

## Cleanup
- Can delete Google Cloud project to stop billing
- Accessible through Google Cloud console's "Manage resources" page