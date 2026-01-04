# Application Architecture

This document describes the standard architecture of the Text Correction application.

## Overview

The application follows a modern **client-server architecture** with clear separation of concerns:

- **Backend**: FastAPI REST API with layered architecture
- **Frontend**: Streamlit web interface with component-based design
- **Shared**: Text correction library (text_basic_check)

## Directory Structure

```
text-basic-check/
├── backend/                      # Backend application
│   ├── __init__.py
│   ├── run.py                   # Entry point
│   └── app/                     # Application package
│       ├── __init__.py
│       ├── main.py              # FastAPI app initialization
│       ├── config.py            # Configuration settings
│       ├── models.py            # Pydantic models
│       ├── routers/             # API routers
│       │   ├── __init__.py
│       │   ├── health.py        # Health check endpoints
│       │   └── files.py         # File upload/download endpoints
│       └── services/            # Business logic layer
│           ├── __init__.py
│           ├── correction.py    # Correction services
│           └── storage.py       # File storage service
│
├── frontend/                     # Frontend application
│   ├── __init__.py
│   ├── app.py                   # Main Streamlit app
│   ├── config.py                # Frontend configuration
│   ├── components/              # UI components
│   │   ├── __init__.py
│   │   ├── sidebar.py           # Sidebar component
│   │   └── upload.py            # Upload component
│   └── utils/                   # Frontend utilities
│       ├── __init__.py
│       └── api_client.py        # API client
│
├── text_basic_check/             # Shared library
│   ├── __init__.py
│   └── spell_checker.py
│
├── start_app.sh                 # Start script (Linux/Mac)
├── start_app.bat                # Start script (Windows)
├── requirements.txt             # Base requirements
├── requirements_api.txt         # API/Frontend requirements
└── requirements_t5_onnx.txt     # T5 model requirements
```

## Backend Architecture

### Layered Architecture

The backend follows a **layered architecture** pattern:

```
┌─────────────────────────────────────┐
│         API Layer (Routers)         │
│  - Health endpoints                 │
│  - File endpoints                   │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│       Service Layer (Services)      │
│  - Spell checking service           │
│  - Grammar correction service       │
│  - File storage service             │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│      Data Layer (Models/Storage)    │
│  - Request/Response models          │
│  - File system storage              │
└─────────────────────────────────────┘
```

### Components

#### 1. Main Application (`backend/app/main.py`)
- FastAPI app initialization
- Middleware configuration (CORS)
- Router registration
- Startup/shutdown events

#### 2. Configuration (`backend/app/config.py`)
- Centralized settings management
- Environment variable support
- Default values
- Type-safe with Pydantic

#### 3. Models (`backend/app/models.py`)
- Request/Response schemas
- Data validation
- Type hints
- Documentation

#### 4. Routers (`backend/app/routers/`)
- **health.py**: Health check, API info
- **files.py**: Upload, download, status, cleanup
- RESTful endpoints
- Dependency injection

#### 5. Services (`backend/app/services/`)
- **correction.py**: Text correction logic
  - `SpellCheckingService`: SymSpell integration
  - `GrammarCorrectionService`: T5 integration
  - `T5ModelService`: Singleton model manager
- **storage.py**: File management
  - `FileStorageService`: Temporary file storage
  - UUID-based file tracking
  - Metadata management

### Design Patterns

- **Singleton**: T5 model manager (avoid reloading)
- **Service Layer**: Business logic separation
- **Dependency Injection**: Router-service decoupling
- **Repository**: File storage abstraction

## Frontend Architecture

### Component-Based Design

The frontend uses a **component-based architecture**:

```
┌─────────────────────────────────────┐
│         Main App (app.py)           │
│  - Page configuration               │
│  - Layout orchestration             │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│       Components (components/)      │
│  - Sidebar component                │
│  - Upload component                 │
│  - Results display                  │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│        Utils (utils/)               │
│  - API client                       │
│  - Helper functions                 │
└─────────────────────────────────────┘
```

### Components

#### 1. Main App (`frontend/app.py`)
- Entry point
- Page configuration
- Component orchestration
- Session state management

#### 2. Configuration (`frontend/config.py`)
- Frontend settings
- API endpoint configuration
- UI preferences

#### 3. Components (`frontend/components/`)
- **sidebar.py**: Settings and status
  - System health check
  - Feature flags
  - About information
- **upload.py**: File upload and results
  - File upload widget
  - Processing button
  - Results display
  - Download buttons

#### 4. Utils (`frontend/utils/`)
- **api_client.py**: Backend communication
  - Health check
  - File upload
  - File download
  - Status checking

### Design Patterns

- **Component Pattern**: Reusable UI components
- **Client-Server**: API communication
- **Observer**: Streamlit session state
- **Facade**: API client abstraction

## API Endpoints

### Health Endpoints

```
GET  /              # API info
GET  /health        # Health check
```

### File Endpoints

```
POST   /files/upload                        # Upload file for correction
GET    /files/download/{file_id}/intermediate  # Download intermediate result
GET    /files/download/{file_id}/final         # Download final result
GET    /files/status/{file_id}                 # Get processing status
DELETE /files/cleanup/{file_id}                # Cleanup files
```

## Data Flow

### Upload and Correction Flow

```
1. User uploads file (Frontend)
        ↓
2. Frontend → POST /files/upload (API)
        ↓
3. API reads file
        ↓
4. SpellCheckingService.correct_text()
   (SymSpell correction)
        ↓
5. Save intermediate.txt
        ↓
6. GrammarCorrectionService.correct_text()
   (T5 correction - if enabled)
        ↓
7. Save final.txt
        ↓
8. Return file_id to Frontend
        ↓
9. Frontend downloads results
        ↓
10. Display and offer downloads
```

### Feature Flag Flow

```
User toggles T5 setting (Frontend)
        ↓
enable_t5 parameter in API call
        ↓
API checks flag:
  - If True: Apply T5 correction
  - If False: Skip T5, use SymSpell result as final
        ↓
Return t5_applied status
        ↓
Frontend adjusts UI labels accordingly
```

## Configuration Management

### Backend Configuration

Environment variables with `APP_` prefix:
- `APP_API_HOST`: API host (default: 0.0.0.0)
- `APP_API_PORT`: API port (default: 8000)
- `APP_T5_MODEL_DIR`: T5 model directory
- `APP_ENABLE_T5_BY_DEFAULT`: Default T5 state

### Frontend Configuration

Environment variables with `FRONTEND_` prefix:
- `FRONTEND_API_URL`: Backend URL (default: http://localhost:8000)
- `FRONTEND_APP_TITLE`: App title
- `FRONTEND_LAYOUT`: Streamlit layout

### Example .env file

```bash
# Backend
APP_API_HOST=0.0.0.0
APP_API_PORT=8000
APP_T5_MODEL_DIR=t5-small-onnx-q

# Frontend
FRONTEND_API_URL=http://localhost:8000
FRONTEND_APP_TITLE=Text Correction Tool
```

## Running the Application

### Development Mode

**Option 1: Separate terminals**

Terminal 1 (Backend):
```bash
python -m backend.run
```

Terminal 2 (Frontend):
```bash
streamlit run frontend/app.py
```

**Option 2: Start script**

```bash
./start_app.sh      # Linux/Mac
start_app.bat       # Windows
```

### Production Mode

**Using Gunicorn (Backend)**:
```bash
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Using Docker**:
```bash
docker-compose up
```

## Testing

### Backend Tests

```bash
pytest backend/tests/
```

### Frontend Tests

```bash
pytest frontend/tests/
```

### Integration Tests

```bash
pytest tests/integration/
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt -r requirements_api.txt -r requirements_t5_onnx.txt

EXPOSE 8000 8501

CMD ["sh", "-c", "python -m backend.run & streamlit run frontend/app.py --server.address=0.0.0.0"]
```

### Kubernetes Deployment

- Backend: Deployment + Service
- Frontend: Deployment + Service + Ingress
- Storage: PersistentVolumeClaim for temp files

## Security Considerations

### Implemented
- ✅ Input validation (file type, encoding)
- ✅ CORS configuration
- ✅ File size limits (configurable)
- ✅ Temporary file cleanup
- ✅ Error handling

### Recommended for Production
- 🔒 Authentication/Authorization
- 🔒 Rate limiting
- 🔒 HTTPS/TLS
- 🔒 API key management
- 🔒 Input sanitization
- 🔒 Audit logging

## Performance

### Optimization Strategies

1. **Model Loading**: Singleton pattern (load once)
2. **File Storage**: Temporary filesystem (fast I/O)
3. **Text Chunking**: Process long texts in chunks
4. **Async Operations**: FastAPI async endpoints
5. **Caching**: Consider Redis for results

### Expected Performance

- SymSpell: ~1ms per word
- T5 (greedy): 100-400ms per sentence
- Upload/Download: Network dependent
- Total pipeline: 500ms-2s for typical text

## Monitoring

### Metrics to Track

- API response times
- Error rates
- File processing times
- Model inference times
- Storage usage
- Active users

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Future Enhancements

### Planned Features
- [ ] User authentication
- [ ] Batch processing
- [ ] Custom dictionaries
- [ ] Multiple language support
- [ ] Result history
- [ ] Real-time correction
- [ ] Collaborative editing

### Technical Improvements
- [ ] Redis caching
- [ ] PostgreSQL for metadata
- [ ] Celery for async tasks
- [ ] WebSocket for real-time updates
- [ ] GraphQL API
- [ ] Microservices architecture

## Contributing

### Code Style

- **Backend**: PEP 8, type hints, docstrings
- **Frontend**: Component-based, clear naming
- **Tests**: Pytest, 80%+ coverage

### Pull Request Process

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit PR with clear description

## License

MIT License - See LICENSE file for details

---

**Last Updated**: January 3, 2026  
**Version**: 2.0.0 (Restructured Architecture)
