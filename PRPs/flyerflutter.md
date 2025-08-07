name: "Canadian Grocery Flyer Comparison App - Production Ready Implementation"
description: |

## Purpose
Production-ready Canadian grocery flyer comparison application that detects user location, finds nearby stores, fetches weekly flyers, and enables price comparison across multiple grocery chains with mobile-first React frontend and FastAPI backend.

## Core Principles
1. **Context is King**: All necessary documentation references included
2. **Validation Loops**: Executable tests and lints for iterative refinement
3. **Information Dense**: Uses researched patterns and official documentation
4. **Progressive Success**: Start with core functionality, validate, then enhance
5. **Global rules**: Follow all rules in CLAUDE.md

---

## Goal
Build a fully-functional grocery flyer comparison app that:
- Automatically detects user location and saves to localStorage
- Discovers nearby grocery stores using Google Places API
- Fetches weekly flyer data using Flipp API (Reebee alternative)
- Caches flyer data in SQLite with weekly refresh via cron job
- Compares prices across stores showing cheapest options
- Provides "Get Directions" functionality via Google Maps
- Allows user filtering (favorite/blocked stores, hidden categories)
- Dockerized for one-command deployment on Railway/Render/Fly.io/GCP

## Why
- **Business Value**: Helps Canadian consumers save money by comparing grocery prices across stores
- **User Impact**: Simplifies weekly grocery planning with location-aware deals
- **Problem Solved**: Eliminates manual flyer checking across multiple stores
- **Integration**: Leverages existing APIs for comprehensive coverage

## What
### User-Visible Behavior:
- Location detection on first visit
- List of nearby grocery stores with distances
- Weekly deals sorted by product/category
- Price comparison showing savings
- Direct navigation to stores
- Persistent filter preferences

### Technical Requirements:
- FastAPI backend with async support
- SQLite database with SQLAlchemy ORM
- React frontend with Tailwind CSS
- Docker containerization
- Environment-based configuration
- Weekly automated updates

### Success Criteria
- [ ] Location detection works and persists
- [ ] Nearby stores load within 2 seconds
- [ ] Flyer data updates weekly automatically
- [ ] Price comparison shows accurate savings
- [ ] Mobile UI is responsive and fast
- [ ] Docker container deploys successfully
- [ ] All tests pass with >80% coverage

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- docfile: research/fastapi/README.md
  why: Complete FastAPI patterns, async handling, dependency injection
  
- docfile: research/pydantic/README.md
  why: Data validation, BaseModel patterns, serialization
  
- docfile: research/sqlalchemy/README.md
  why: SQLite setup, ORM patterns, async sessions
  
- docfile: research/google-places/01-overview.md
  why: New Places API endpoints and authentication
  
- docfile: research/google-places/02-nearby-search.md
  why: Nearby search implementation with field masking
  
- docfile: research/google-directions/02-get-directions.md
  why: Directions API parameters and response handling
  
- docfile: research/reebee-api/02-flipp-api-alternative.md
  why: Flipp API endpoints and implementation (Reebee alternative)
  
- docfile: research/react/01-react-fundamentals.md
  why: Component patterns, hooks, state management
  
- docfile: research/tailwind/01-overview.md
  why: Utility-first CSS approach, responsive design
  
- docfile: research/docker/04-fastapi-docker.md
  why: FastAPI-specific Docker patterns
  
- url: https://backflipp.wishabi.com/flipp
  why: Flipp API endpoints for Canadian grocery data
  
- url: https://places.googleapis.com/v1/places:searchNearby
  why: Google Places nearby search endpoint
  
- critical: Flipp API is unofficial but accessible - implement rate limiting
- critical: Google Places requires field masking to control costs
- critical: Use SQLAlchemy 2.0 syntax with Mapped[] annotations
- critical: React Context for global state, localStorage for persistence
```

### Current Codebase tree
```bash
flyerflutter/
├── CLAUDE.md
├── initial.md
├── PRPs/
│   └── templates/
│       └── prp_base.md
└── research/
    ├── fastapi/
    ├── pydantic/
    ├── sqlalchemy/
    ├── google-places/
    ├── google-directions/
    ├── reebee-api/
    ├── react/
    ├── tailwind/
    ├── docker/
    └── deployment/
```

### Desired Codebase tree with files to be added
```bash
flyerflutter/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # SQLAlchemy setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── store.py         # Store ORM model
│   │   ├── flyer_item.py    # FlyerItem ORM model
│   │   └── user_filters.py  # UserFilters ORM model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── store.py         # Pydantic schemas
│   │   ├── flyer_item.py    # Pydantic schemas
│   │   └── user_filters.py  # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── google_service.py    # Google APIs integration
│   │   ├── flyer_service.py     # Flipp API integration
│   │   └── scheduler.py         # Weekly update scheduler
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_services.py
│       └── test_api.py
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx          # Main React app
│   │   ├── index.js         # Entry point
│   │   ├── index.css        # Tailwind imports
│   │   ├── components/
│   │   │   ├── StoreCard.jsx
│   │   │   ├── DealList.jsx
│   │   │   ├── FilterPanel.jsx
│   │   │   └── LocationDetector.jsx
│   │   ├── contexts/
│   │   │   └── FilterContext.jsx
│   │   ├── hooks/
│   │   │   ├── useLocation.js
│   │   │   └── useLocalStorage.js
│   │   └── services/
│   │       └── api.js       # Backend API client
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── Dockerfile               # Multi-stage build
├── docker-compose.yml       # Local development
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
└── README.md              # Setup instructions
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: Flipp API has no official docs - use rate limiting
# Example: Max 10 requests per second to avoid blocks

# CRITICAL: Google Places API requires field masks for cost control
# Example: fields=places.displayName,places.location

# CRITICAL: SQLAlchemy 2.0 uses new syntax
# Example: Use Mapped[] instead of Column()

# CRITICAL: Pydantic v2 has different validator syntax
# Example: Use @field_validator instead of @validator

# CRITICAL: React 18+ requires ReactDOM.createRoot
# Example: Not ReactDOM.render()

# CRITICAL: APScheduler needs proper shutdown handling
# Example: Register shutdown event in FastAPI
```

## Implementation Blueprint

### Data models and structure

Create the core data models with SQLAlchemy ORM and Pydantic schemas:

```python
# ORM Models (SQLAlchemy 2.0 style)
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

class Store(Base):
    __tablename__ = "stores"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    place_id: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    address: Mapped[str]
    lat: Mapped[float]
    lng: Mapped[float]
    
class FlyerItem(Base):
    __tablename__ = "flyer_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"))
    name: Mapped[str]
    category: Mapped[str]
    price: Mapped[float]
    image: Mapped[Optional[str]]
    sale_start: Mapped[datetime]
    sale_end: Mapped[datetime]

# Pydantic Schemas
from pydantic import BaseModel, field_validator

class StoreSchema(BaseModel):
    id: int
    place_id: str
    name: str
    address: str
    lat: float
    lng: float
    
    @field_validator('lat', 'lng')
    def validate_coordinates(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Invalid coordinate')
        return v
```

### List of tasks to be completed in order

```yaml
Task 1: Setup Backend Structure
CREATE backend/__init__.py
CREATE backend/config.py:
  - Load environment variables with python-dotenv
  - Define settings with defaults
  - Include: GOOGLE_API_KEY, DATABASE_URL, FLIPP_BASE_URL

Task 2: Database Setup
CREATE backend/database.py:
  - SQLAlchemy engine with SQLite
  - Session factory with proper lifecycle
  - Base declarative class
CREATE backend/models/*.py:
  - PATTERN from: research/sqlalchemy/03-orm-quickstart.md
  - Use Mapped[] annotations
  - Define relationships

Task 3: Pydantic Schemas
CREATE backend/schemas/*.py:
  - PATTERN from: research/pydantic/02-models.md
  - Input/Output separation
  - Field validators for coordinates
  - Response models with filtering

Task 4: Google Service Integration
CREATE backend/services/google_service.py:
  - PATTERN from: research/google-places/02-nearby-search.md
  - Implement nearby_search with field masking
  - Add get_directions method
  - Handle API errors and rate limits

Task 5: Flipp Service Integration  
CREATE backend/services/flyer_service.py:
  - PATTERN from: research/reebee-api/02-flipp-api-alternative.md
  - Implement get_flyers_by_postal
  - Parse flyer items with categories
  - Add caching logic

Task 6: Scheduler Setup
CREATE backend/services/scheduler.py:
  - Use APScheduler with AsyncIOScheduler
  - Weekly flyer refresh job
  - Proper shutdown handling
  - Error recovery

Task 7: API Routes
CREATE backend/api/routes.py:
  - PATTERN from: research/fastapi/03-first-steps.md
  - GET /api/stores endpoint
  - GET /api/deals endpoint
  - POST /api/filters endpoint
  - Dependency injection for DB

Task 8: FastAPI Application
CREATE backend/main.py:
  - FastAPI app initialization
  - CORS middleware setup
  - Static file serving
  - Scheduler integration
  - Lifespan events

Task 9: Frontend Setup
CREATE frontend/package.json:
  - React 18+ dependencies
  - Tailwind CSS
  - Vite for bundling
  - Axios for API calls
CREATE frontend/vite.config.js:
  - Proxy API calls to backend
  - Build optimization

Task 10: React Components
CREATE frontend/src/components/*.jsx:
  - PATTERN from: research/react/01-react-fundamentals.md
  - Functional components with hooks
  - Mobile-first responsive design
  - Error boundaries

Task 11: State Management
CREATE frontend/src/contexts/FilterContext.jsx:
  - PATTERN from: research/react/05-usecontext.md
  - Global filter state
  - localStorage persistence
  - Provider wrapper

Task 12: Custom Hooks
CREATE frontend/src/hooks/*.js:
  - useLocation for geolocation
  - useLocalStorage for persistence
  - Error handling

Task 13: API Client
CREATE frontend/src/services/api.js:
  - Axios instance with base URL
  - Request/response interceptors
  - Error handling
  - Retry logic

Task 14: Docker Configuration
CREATE Dockerfile:
  - PATTERN from: research/docker/04-fastapi-docker.md
  - Multi-stage build
  - Frontend build stage
  - Backend production stage
  - Environment variables
CREATE docker-compose.yml:
  - Service definitions
  - Volume mounts
  - Environment configuration

Task 15: Testing
CREATE backend/tests/*.py:
  - Unit tests for services
  - API endpoint tests
  - Mock external APIs
  - Database fixtures
```

### Per task pseudocode

```python
# Task 4: Google Service
class GoogleService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://places.googleapis.com/v1"
        
    async def nearby_search(self, lat: float, lng: float, radius: int = 5000):
        # PATTERN: Use field masking from research/google-places/02-nearby-search.md
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types"
        }
        
        # CRITICAL: Include grocery store types
        body = {
            "includedTypes": ["grocery_store", "supermarket"],
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": radius
                }
            }
        }
        
        # Rate limiting
        async with rate_limiter:
            response = await httpx.post(url, json=body, headers=headers)
            
        return self._parse_places(response.json())

# Task 5: Flipp Service  
class FlippService:
    async def get_flyers_by_postal(self, postal_code: str):
        # PATTERN: From research/reebee-api/02-flipp-api-alternative.md
        params = {
            "locale": "en-ca",
            "postal_code": postal_code,
            "merchants": "walmart,loblaws,metro,sobeys"
        }
        
        # GOTCHA: Unofficial API - add retry logic
        @retry(attempts=3, backoff=2)
        async def _fetch():
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{FLIPP_BASE_URL}/items/search",
                    params=params
                )
                return response.json()
                
        return await _fetch()

# Task 11: Filter Context
const FilterContext = createContext();

export const FilterProvider = ({ children }) => {
    // PATTERN: localStorage persistence
    const [filters, setFilters] = useLocalStorage('userFilters', {
        favoriteStores: [],
        blockedStores: [],
        hiddenCategories: []
    });
    
    const updateFilters = useCallback((newFilters) => {
        setFilters(prev => ({ ...prev, ...newFilters }));
    }, [setFilters]);
    
    return (
        <FilterContext.Provider value={{ filters, updateFilters }}>
            {children}
        </FilterContext.Provider>
    );
};
```

### Integration Points
```yaml
DATABASE:
  - migration: "alembic init alembic && alembic revision --autogenerate"
  - tables: "stores, flyer_items, user_filters"
  - indexes: "CREATE INDEX idx_flyer_store ON flyer_items(store_id)"
  
CONFIG:
  - add to: backend/config.py
  - pattern: |
      GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
      DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./flyers.db')
      FLIPP_BASE_URL = os.getenv('FLIPP_BASE_URL', 'https://backflipp.wishabi.com/flipp')
      
ROUTES:
  - add to: backend/main.py
  - pattern: |
      app.include_router(api_router, prefix="/api")
      app.mount("/", StaticFiles(directory="frontend/dist", html=True))
      
SCHEDULER:
  - add to: backend/main.py
  - pattern: |
      @asynccontextmanager
      async def lifespan(app: FastAPI):
          scheduler.start()
          yield
          scheduler.shutdown()
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Backend validation
cd backend
ruff check . --fix           # Auto-fix Python issues
mypy .                       # Type checking

# Frontend validation  
cd frontend
npm run lint                 # ESLint check
npm run type-check          # TypeScript if used

# Expected: No errors. Fix any issues before proceeding.
```

### Level 2: Unit Tests
```python
# CREATE backend/tests/test_services.py
@pytest.mark.asyncio
async def test_google_nearby_search():
    """Test Google Places nearby search"""
    service = GoogleService(api_key="test_key")
    with mock.patch('httpx.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "places": [{"displayName": {"text": "Metro"}}]
        }
        
        results = await service.nearby_search(45.5, -73.5)
        assert len(results) > 0
        assert results[0]["name"] == "Metro"

@pytest.mark.asyncio
async def test_flipp_service_retry():
    """Test Flipp API retry logic"""
    service = FlippService()
    with mock.patch('httpx.AsyncClient.get') as mock_get:
        mock_get.side_effect = [httpx.TimeoutException, {"items": []}]
        
        result = await service.get_flyers_by_postal("K1A0B1")
        assert mock_get.call_count == 2
        
# CREATE frontend/src/components/__tests__/StoreCard.test.jsx
import { render, screen } from '@testing-library/react';
import StoreCard from '../StoreCard';

test('renders store information', () => {
    const store = {
        name: 'Test Store',
        address: '123 Main St',
        distance: 1.5
    };
    
    render(<StoreCard store={store} />);
    expect(screen.getByText('Test Store')).toBeInTheDocument();
    expect(screen.getByText('1.5 km')).toBeInTheDocument();
});
```

```bash
# Run backend tests
cd backend
python -m pytest tests/ -v

# Run frontend tests
cd frontend
npm test

# If failing: Read errors, fix code, re-run
```

### Level 3: Integration Test
```bash
# Start services
docker-compose up -d

# Test location endpoint
curl -X GET "http://localhost:8000/api/stores?lat=45.5017&lng=-73.5673"
# Expected: JSON array of nearby stores

# Test deals endpoint
curl -X GET "http://localhost:8000/api/deals?lat=45.5017&lng=-73.5673"
# Expected: JSON array of flyer items grouped by store

# Test frontend
open http://localhost:3000
# Expected: Location prompt, then store list with deals

# Check logs
docker-compose logs -f backend
# Expected: No errors, scheduler running
```

## Final Validation Checklist
- [ ] All tests pass: `pytest backend/tests/ -v && npm test --prefix frontend`
- [ ] No linting errors: `ruff check backend/ && npm run lint --prefix frontend`
- [ ] No type errors: `mypy backend/`
- [ ] Manual test successful: App loads, shows stores and deals
- [ ] Error cases handled gracefully (no location, API failures)
- [ ] Logs are informative but not verbose
- [ ] Docker container builds and runs successfully
- [ ] Environment variables documented in .env.example

## Docker Deployment Commands
```bash
# Build and run locally
docker build -t flyerflutter .
docker run -p 8000:8000 --env-file .env flyerflutter

# Deploy to Railway
railway up

# Deploy to Render
# Push to GitHub, connect repo in Render dashboard

# Deploy to Fly.io
flyctl launch
flyctl deploy

# Deploy to Google Cloud Run
gcloud run deploy flyerflutter --source .
```

---

## Anti-Patterns to Avoid
- ❌ Don't hardcode API keys - use environment variables
- ❌ Don't skip field masking on Google APIs - costs will explode
- ❌ Don't fetch all flyers at once - paginate and cache
- ❌ Don't use synchronous requests in async context
- ❌ Don't store sensitive user data - only preferences
- ❌ Don't ignore rate limits - implement backoff
- ❌ Don't use old SQLAlchemy syntax - use 2.0 patterns
- ❌ Don't forget CORS configuration for production

---

## Confidence Score: 9/10

This PRP provides comprehensive context with:
- Exact API endpoints and patterns from research
- Production-ready error handling and rate limiting
- Complete Docker deployment configuration
- Validation gates at every level
- References to all necessary documentation

The implementation should succeed in one pass with the provided context and validation loops.