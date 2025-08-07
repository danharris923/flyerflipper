# FlyerFlutter 🛒

**Canadian Grocery Flyer Comparison Platform**

FlyerFlutter helps Canadian shoppers find the best grocery deals by comparing weekly flyers from major grocery stores. Simply set your location, and discover the lowest prices on your favorite products nearby.

## ✨ Features

- 🗺️ **Location-based Store Discovery** - Find grocery stores near you using Google Places API
- 🎯 **Smart Deal Comparison** - Compare prices across multiple stores automatically
- 🔍 **Advanced Filtering** - Filter by price range, categories, distance, and discount percentage
- 📱 **Mobile-First Design** - Responsive UI optimized for all devices
- ⚡ **Real-time Updates** - Weekly flyer data refreshed automatically
- 🏪 **Store Preferences** - Mark favorite stores or hide unwanted ones
- 💾 **Local Storage** - Remember your preferences and location

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **FastAPI** - High-performance async web framework
- **SQLAlchemy 2.0** - Modern Python ORM with async support
- **Pydantic v2** - Data validation and serialization
- **APScheduler** - Background task scheduling
- **SQLite** - Lightweight database for development

### Frontend (React + Vite)
- **React 18** - Modern UI library with hooks and context
- **Vite** - Lightning-fast build tool and dev server
- **Tailwind CSS** - Utility-first styling framework
- **Lucide Icons** - Beautiful, customizable icons
- **Axios** - HTTP client with interceptors

### Data Sources
- **Google Places API** - Store locations and business information
- **Unofficial Flipp API** - Grocery flyer data (no credentials required)

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended)
- **Node.js 18+** and **Python 3.11+** (for local development)
- **Google Places API Key** (required)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd flyerflutter
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google Places API key
   ```

3. **Start with Docker Compose**
   ```bash
   # Development mode (with hot reload)
   docker-compose up --build
   
   # Production mode
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Option 2: Local Development

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r ../requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Development Servers**
   ```bash
   # Terminal 1: Backend
   cd backend
   python -m uvicorn main:app --reload --port 8000
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## 🔧 Configuration

### Required Environment Variables

```env
# Google Places API Key (Required)
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here

# Database
DATABASE_URL=sqlite:///data/flyerflutter.db

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Getting a Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable these APIs:
   - Places API (New)
   - Geocoding API
4. Create credentials → API key
5. Restrict the key to your APIs and domains (recommended)

## 📁 Project Structure

```
flyerflutter/
├── backend/                 # Python FastAPI backend
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic services
│   ├── api/                # API routes
│   ├── config.py           # Configuration
│   ├── database.py         # Database setup
│   └── main.py            # FastAPI application
├── frontend/               # React frontend
│   ├── public/            # Static assets
│   └── src/
│       ├── components/    # React components
│       ├── contexts/      # React contexts
│       ├── hooks/         # Custom hooks
│       ├── services/      # API client
│       └── App.jsx        # Main app component
├── tests/                 # Test files
├── docker-compose.yml     # Docker development setup
├── docker-compose.prod.yml # Docker production setup
├── Dockerfile            # Multi-stage Docker build
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🧪 Testing

### Run Backend Tests
```bash
# Using Docker
docker-compose exec app python -m pytest

# Local development
cd backend
python -m pytest tests/ -v
```

### Run Frontend Tests
```bash
# Using Docker
docker-compose exec app npm run test

# Local development
cd frontend
npm run test
```

### Linting and Type Checking
```bash
# Python linting
ruff check backend/
mypy backend/

# JavaScript linting
npm run lint
npm run type-check
```

## 🚀 Deployment

### Docker Production Deployment

1. **Prepare production environment**
   ```bash
   cp .env.example .env
   # Set ENV=production and configure production values
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
   ```

3. **Setup SSL (recommended)**
   ```bash
   # Add SSL certificates to ./ssl/ directory
   # Configure nginx.conf for HTTPS
   ```

### Environment-Specific Commands

```bash
# Development
docker-compose up --build

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f app

# Database backup (production)
docker-compose exec backup /bin/sh
```

## 🔍 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `GET /health` - Health check
- `GET /stores/nearby` - Find nearby stores
- `GET /deals` - Get deals with filtering
- `POST /deals/search` - Search deals by query
- `GET /stores/{store_id}/deals` - Get deals for specific store

## 🛠️ Development

### Adding New Features

1. **Backend Changes**
   - Add models in `backend/models/`
   - Create schemas in `backend/schemas/`
   - Implement services in `backend/services/`
   - Add routes in `backend/api/`

2. **Frontend Changes**
   - Create components in `frontend/src/components/`
   - Add hooks in `frontend/src/hooks/`
   - Update contexts in `frontend/src/contexts/`

3. **Testing**
   - Add tests in `tests/`
   - Update documentation

### Code Style

- **Python**: Follow PEP8, use Black formatter, Ruff linter
- **JavaScript**: ESLint + Prettier configuration
- **Commits**: Use conventional commit messages
- **Documentation**: Update README and API docs

## 📊 Monitoring and Logging

### Health Checks
- Application: `GET /health`
- Database: Included in health check
- External APIs: Connection testing available

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log files: `logs/flyerflutter.log`

### Metrics (Production)
- Prometheus metrics endpoint: `/metrics`
- Custom business metrics included
- Docker health checks configured

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and add tests
4. Run linting and tests: `npm run lint && python -m pytest`
5. Commit changes: `git commit -m 'feat: add amazing feature'`
6. Push to branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Google API Key Issues**
   - Ensure Places API and Geocoding API are enabled
   - Check API key restrictions
   - Verify billing is enabled (required for Google APIs)

2. **Docker Build Fails**
   ```bash
   # Clean Docker cache and rebuild
   docker system prune -f
   docker-compose build --no-cache
   ```

3. **CORS Errors**
   - Check CORS_ORIGINS in .env
   - Ensure frontend URL matches CORS configuration

4. **Database Issues**
   ```bash
   # Reset database
   rm -rf data/
   docker-compose restart app
   ```

### Getting Help

- Check the [Issues](../../issues) page
- Review API documentation at `/docs`
- Enable debug logging: `DEBUG=true LOG_LEVEL=debug`

## 🔄 Changelog

### v1.0.0 (Current)
- Initial release
- Location-based store discovery
- Deal comparison and filtering
- Mobile-responsive design
- Docker deployment support
- Unofficial Flipp API integration

---

**Built with ❤️ for Canadian grocery shoppers**