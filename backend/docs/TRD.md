# Technical Requirements Document (TRD)
## TodList - Web-based Todo List Application

**Version:** 1.0  
**Date:** November 2024  
**Status:** Draft

---

## 1. System Architecture

### 1.1 Architecture Overview

TodList will implement a **three-tier architecture** with clear separation of concerns:

1. **Presentation Tier (Frontend):** React-based SPA (Single Page Application)
2. **Application Tier (Backend):** FastAPI-based RESTful API server
3. **Data Tier:** PostgreSQL database with Redis caching layer

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Tier                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         React SPA (Nginx served)                     │   │
│  │    ┌──────────┐  ┌──────────┐  ┌──────────┐       │   │
│  │    │   UI     │  │  State   │  │   API    │       │   │
│  │    │Components│  │Management│  │  Client  │       │   │
│  │    └──────────┘  └──────────┘  └──────────┘       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Tier                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Load Balancer (Nginx)                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  FastAPI     │  │  FastAPI     │  │  FastAPI     │     │
│  │  Instance 1  │  │  Instance 2  │  │  Instance N  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Tier                               │
│  ┌─────────────────┐              ┌─────────────────┐      │
│  │   PostgreSQL    │              │     Redis       │      │
│  │   Primary       │◄────────────►│   Cache Layer   │      │
│  │                 │              │                 │      │
│  └─────────────────┘              └─────────────────┘      │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                       │
│  │   PostgreSQL    │                                       │
│  │   Replica       │                                       │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Key Architecture Decisions

- **Microservices-Ready:** While starting as a monolith, the architecture supports future decomposition
- **Stateless Backend:** All session state stored in Redis for horizontal scalability
- **API-First Design:** Complete separation between frontend and backend
- **Caching Strategy:** Redis for session management and frequently accessed data
- **Database Replication:** Master-slave configuration for read scalability

---

## 2. Frontend (Client-Side)

### 2.1 Framework and Language

- **Framework:** React 18.2+
- **Language:** TypeScript 5.0+
- **Runtime:** Node.js 18+ (development)

### 2.2 State Management

- **Primary:** Redux Toolkit 2.0+
- **Async State:** RTK Query for API calls
- **Local State:** React hooks (useState, useReducer)

**State Structure:**
```typescript
interface AppState {
  auth: {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
  };
  todos: {
    items: Todo[];
    filters: FilterState;
    pagination: PaginationState;
    loading: boolean;
    error: string | null;
  };
  tags: {
    items: Tag[];
    loading: boolean;
  };
  ui: {
    theme: 'light' | 'dark';
    sidebarOpen: boolean;
    notifications: Notification[];
  };
}
```

### 2.3 Routing

- **Router:** React Router v6+
- **Route Structure:**
```typescript
const routes = [
  { path: '/login', component: Login, public: true },
  { path: '/register', component: Register, public: true },
  { path: '/dashboard', component: Dashboard, protected: true },
  { path: '/todos', component: TodoList, protected: true },
  { path: '/todos/:id', component: TodoDetail, protected: true },
  { path: '/tags', component: TagManager, protected: true },
  { path: '/settings', component: Settings, protected: true },
];
```

### 2.4 Styling

- **CSS Framework:** Tailwind CSS 3.3+
- **Component Library:** Headless UI
- **Icons:** Heroicons
- **Animations:** Framer Motion
- **Theme System:** CSS variables for light/dark mode

### 2.5 API Communication

- **HTTP Client:** Axios with interceptors
- **API Integration:** RTK Query for caching and synchronization
- **WebSocket:** Socket.io-client for real-time updates (future)

**API Client Configuration:**
```typescript
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
apiClient.interceptors.request.use((config) => {
  const token = store.getState().auth.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      store.dispatch(logout());
    }
    return Promise.reject(error);
  }
);
```

### 2.6 Build Tool

- **Bundler:** Vite 5.0+
- **Package Manager:** pnpm
- **Linting:** ESLint with Airbnb config
- **Formatting:** Prettier
- **Testing:** Jest + React Testing Library
- **E2E Testing:** Cypress

**Build Configuration:**
```javascript
// vite.config.ts
export default {
  plugins: [react(), tsconfigPaths()],
  build: {
    target: 'es2015',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          redux: ['@reduxjs/toolkit', 'react-redux'],
        },
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
};
```

---

## 3. Backend (Server-Side)

### 3.1 Framework and Language

- **Framework:** FastAPI 0.104+
- **Language:** Python 3.11+
- **ASGI Server:** Uvicorn with Gunicorn

### 3.2 Authentication Mechanism

- **Method:** JWT (JSON Web Tokens)
- **Library:** python-jose[cryptography]
- **Token Types:** Access Token (15 min) + Refresh Token (7 days)
- **Password Hashing:** bcrypt

**Authentication Flow:**
```python
# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Token Model
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Authentication Dependencies
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user
```

### 3.3 Database Communication

- **ORM:** SQLAlchemy 2.0+
- **Migration Tool:** Alembic
- **Connection Pooling:** SQLAlchemy built-in with asyncpg
- **Query Optimization:** Eager loading, query batching

**Database Configuration:**
```python
# Database URL
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Engine Configuration
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

# Session Factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

### 3.4 High-Level API Specification

**Base URL Structure:** `/api/v1`

**Common Response Format:**
```python
class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

**Authentication Endpoints:**
```python
@router.post("/auth/register", response_model=APIResponse[Token])
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[Token]:
    # Validate email uniqueness
    # Hash password
    # Create user
    # Generate tokens
    # Return tokens

@router.post("/auth/login", response_model=APIResponse[Token])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[Token]:
    # Verify credentials
    # Generate tokens
    # Log login event
    # Return tokens

@router.post("/auth/refresh", response_model=APIResponse[Token])
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> APIResponse[Token]:
    # Validate refresh token
    # Generate new access token
    # Optionally rotate refresh token
    # Return new tokens
```

**Todo Endpoints:**
```python
@router.get("/todos", response_model=APIResponse[PaginatedResponse[TodoRead]])
async def list_todos(
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=100),
    status: Optional[TodoStatus] = None,
    priority: Optional[Priority] = None,
    tag: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", regex="^(created_at|due_date|priority)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[PaginatedResponse[TodoRead]]:
    # Build query with filters
    # Apply pagination
    # Return paginated results

@router.post("/todos", response_model=APIResponse[TodoRead])
async def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[TodoRead]:
    # Validate input
    # Create todo
    # Handle tags
    # Return created todo

@router.put("/todos/{todo_id}", response_model=APIResponse[TodoRead])
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> APIResponse[TodoRead]:
    # Verify ownership
    # Update fields
    # Handle tag changes
    # Return updated todo
```

**Middleware Stack:**
```python
app = FastAPI(title="TodList API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
app.add_middleware(
    RateLimitMiddleware,
    rate_limit="100/minute",
    key_func=get_remote_address,
)

# Request ID
app.add_middleware(RequestIDMiddleware)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security Headers
app.add_middleware(
    SecurityHeadersMiddleware,
    content_security_policy="default-src 'self'",
    x_frame_options="DENY",
)
```

---

## 4. Database

### 4.1 Database System

- **Primary Database:** PostgreSQL 15+
- **Extensions Required:** 
  - `uuid-ossp` for UUID generation
  - `pg_trgm` for full-text search
  - `btree_gin` for composite indexes

### 4.2 Data Models

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    is_verified BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-