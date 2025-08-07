# Render Deployment

## Deployment Configuration
- Select "Web Service" in Render Dashboard
- Specify language/runtime
- Provide build and start commands
- Automatic deployment on branch pushes

## Build & Start Commands Examples
### Build Commands:
- `yarn`
- `npm install`
- `bun install`

### Start Commands:
- `node app.js`
- `npm start`
- `bun start`

## Deployment Patterns
- "Every push to your linked branch automatically builds and deploys"
- Failed builds are automatically rolled back
- Services get a default `onrender.com` URL

## Environment Configuration
- Can configure Node.js version explicitly
- Supports environment variables
- Supports connecting GitHub repositories

## Key Deployment Steps
1. Connect GitHub repository
2. Select web service type
3. Configure build/start commands
4. Deploy

## For FastAPI + React Applications
- Can deploy both services separately
- Supports different runtimes (Python for FastAPI, Node.js for React)
- Environment variable configuration for each service
- Custom domain support

The documentation suggests flexibility in build processes while providing a standardized deployment workflow across different project types.