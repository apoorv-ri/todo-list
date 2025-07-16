# Technical System Design (TSD)
## TodList - Web-based Todo List Application

**Version:** 1.0  
**Date:** November 2024  
**Based on PRD Version:** 1.0

---

## 1. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                   FRONTEND                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │   React App     │  │   Redux Store   │  │  Service Layer  │            │
│  │  Components     │  │   State Mgmt    │  │   API Client    │            │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘            │
│           └─────────────────────┴─────────────────────┘                     │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │ HTTPS (REST API)
                                    │
┌───────────────────────────────────┴─────────────────────────────────────────┐
│                                   BACKEND                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │   Nginx         │  │    FastAPI      │  │  Redis Cache    │            │
│  │ Reverse Proxy   │──│   Application   │──│  Session Store  │            │
│  └─────────────────┘  └────────┬────────┘  └─────────────────┘            │
│                                │                                            │
│  ┌─────────────────────────────┴────────────────────────────┐              │
│  │                     Business Logic Layer                  │              │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │              │
│  │  │Auth Service  │  │Todo Service  │  │ Tag Service  │  │              │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │              │
│  └───────────────────────────┬──────────────────────────────┘              │
│                              │                                              │
│  ┌───────────────────────────┴──────────────────────────────┐              │
│  │                      Data Access Layer                    │              │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │              │
│  │  │ User Repo    │  │ Todo Repo    │  │  Tag Repo    │  │              │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │              │
│  └───────────────────────────┬──────────────────────────────┘              │
└──────────────────────────────┼──────────────────────────────────────────────┘
                               │ SQL Queries
                               │
┌──────────────────────────────┴──────────────────────────────────────────────┐
│                                DATABASE                                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │   PostgreSQL    │  │   Connection    │  │    Backup       │            │
│  │   Primary DB    │──│      Pool       │──│   Storage       │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 2. Component Design

### 2.1 Frontend Components

```
frontend/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.jsx
│   │   │   ├── RegisterForm.jsx
│   │   │   └── PasswordReset.jsx
│   │   ├── todos/
│   │   │   ├── TodoList.jsx
│   │   │   ├── TodoItem.jsx
│   │   │   ├── TodoForm.jsx
│   │   │   ├── TodoFilters.jsx
│   │   │   └── TodoSearch.jsx
│   │   ├── tags/
│   │   │   ├── TagManager.jsx
│   │   │   ├── TagSelector.jsx
│   │   │   └── TagBadge.jsx
│   │   └── common/
│   │       ├── Header.jsx
│   │       ├── Navigation.jsx
│   │       ├── Pagination.jsx
│   │       └── ErrorBoundary.jsx
│   ├── services/
│   │   ├── api.js
│   │   ├── auth.service.js
│   │   ├── todo.service.js
│   │   └── tag.service.js
│   ├── store/
│   │   ├── auth/
│   │   ├── todos/
│   │   └── tags/
│   └── utils/
│       ├── validators.js
│       ├── formatters.js
│       └── constants.js
```

### 2.2 Backend Components

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── todos.py
│   │   │   │   └── tags.py
│   │   │   └── api.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   │   ├── user.py
│   │   ├── todo.py
│   │   └── tag.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── todo.py
│   │   └── tag.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── todo_service.py
│   │   └── tag_service.py
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── todo_repository.py
│   │   └── tag_repository.py
│   └── main.py
```

## 3. API Endpoint Design

### 3.1 Authentication Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/v1/auth/register` | Register new user | `{email, password, name}` | `{user_id, email, token}` |
| POST | `/api/v1/auth/login` | User login | `{email, password}` | `{access_token, refresh_token, user}` |
| POST | `/api/v1/auth/logout` | User logout | - | `{message}` |
| POST | `/api/v1/auth/refresh` | Refresh token | `{refresh_token}` | `{access_token}` |
| POST | `/api/v1/auth/reset-password` | Reset password | `{email}` | `{message}` |
| POST | `/api/v1/auth/change-password` | Change password | `{old_password, new_password}` | `{message}` |

### 3.2 Todo Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/v1/todos` | List todos | Query params: `page, limit, status, priority` | `{todos[], total, page, pages}` |
| POST | `/api/v1/todos` | Create todo | `{title, description, due_date, priority, tags[]}` | `{todo}` |
| GET | `/api/v1/todos/{id}` | Get todo | - | `{todo}` |
| PUT | `/api/v1/todos/{id}` | Update todo | `{title, description, due_date, priority, tags[]}` | `{todo}` |
| DELETE | `/api/v1/todos/{id}` | Delete todo | - | `{message}` |
| PATCH | `/api/v1/todos/{id}/complete` | Toggle completion | - | `{todo}` |
| GET | `/api/v1/todos/search` | Search todos | Query param: `q` | `{todos[], total}` |

### 3.3 Tag Endpoints

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/v1/tags` | List tags | - | `{tags[]}` |
| POST | `/api/v1/tags` | Create tag | `{name, color}` | `{tag}` |
| PUT | `/api/v1/tags/{id}` | Update tag | `{name, color}` | `{tag}` |
| DELETE | `/api/v1/tags/{id}` | Delete tag | - | `{message}` |

## 4. Database Schema Design

```
┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│       users         │         │       todos         │         │       tags          │
├─────────────────────┤         ├─────────────────────┤         ├─────────────────────┤
│ id (PK)            │         │ id (PK)            │         │ id (PK)            │
│ email (UNIQUE)     │         │ user_id (FK)       │         │ user_id (FK)       │
│ password_hash      │         │ title              │         │ name               │
│ name               │         │ description        │         │ color              │
│ is_active          │         │ priority           │         │ created_at         │
│ created_at         │         │ due_date           │         │ updated_at         │
│ updated_at         │         │ is_completed       │         └─────────────────────┘
│ last_login         │         │ completed_at       │                    │
└─────────────────────┘         │ is_deleted         │                    │
           │                    │ deleted_at         │                    │
           │                    │ created_at         │                    │
           │                    │ updated_at         │                    │
           │                    └─────────────────────┘                    │
           │                               │                               │
           └───────────1:N─────────────────┘                               │
                                          │                                │
                                          │                                │
                                          │         ┌─────────────────────┐│
                                          │         │    todo_tags        ││
                                          │         ├─────────────────────┤│
                                          └────N:N──│ todo_id (FK)       ││
                                                    │ tag_id (FK)        ││
                                                    │ created_at         ││
                                                    └─────────────────────┘│
                                                               │           │
                                                               └───────────┘

Database Indexes:
- users: email (UNIQUE), created_at
- todos: user_id, is_completed, is_deleted, due_date, created_at
- tags: user_id, name
- todo_tags: (todo_id, tag_id) UNIQUE
```

## 5. Data Flow Examples

### 5.1 User Login Flow

```
┌──────┐        ┌─────────┐        ┌─────────┐        ┌──────────┐        ┌────────┐
│Client│        │Frontend │        │ FastAPI │        │Auth      │        │Database│
└──┬───┘        └────┬────┘        └────┬────┘        │Service   │        └───┬────┘
   │                 │                   │             └────┬─────┘            │
   │  Enter Creds    │                   │                  │                  │
   ├────────────────>│                   │                  │                  │
   │                 │                   │                  │                  │
   │                 │ POST /auth/login  │                  │                  │
   │                 ├──────────────────>│                  │                  │
   │                 │                   │                  │                  │
   │                 │                   │ Validate Request │                  │
   │                 │                   ├─────────────────>│                  │
   │                 │                   │                  │                  │
   │                 │                   │                  │ Query User       │
   │                 │                   │                  ├─────────────────>│
   │                 │                   │                  │                  │
   │                 │                   │                  │  User Data       │
   │                 │                   │                  │<─────────────────┤
   │                 │                   │                  │                  │
   │                 │                   │                  │Verify Password   │
   │                 │                   │                  ├────┐             │
   │                 │                   │                  │    │             │
   │                 │                   │                  │<───┘             │
   │                 │                   │                  │                  │
   │                 │                   │                  │Generate JWT      │
   │                 │                   │                  ├────┐             │
   │                 │                   │                  │    │             │
   │                 │                   │                  │<───┘             │
   │                 │                   │                  │                  │
   │                 │                   │   JWT Tokens    │                  │
   │                 │                   │<─────────────────┤                  │
   │                 │                   │                  │                  │
   │                 │                   │                  │Update Last Login │
   │                 │                   │                  ├─────────────────>│
   │                 │                   │                  │                  │
   │                 │  Store in State   │                  │                  │
   │                 │<──────────────────┤                  │                  │
   │                 │                   │                  │                  │
   │  Login Success  │                   │                  │                  │
   │<────────────────┤                   │                  │                  │
   │                 │                   │                  │                  │
```

### 5.2 Create Todo Flow

```
┌──────┐        ┌─────────┐        ┌─────────┐        ┌──────────┐        ┌────────┐
│Client│        │Frontend │        │ FastAPI │        │Todo      │        │Database│
└──┬───┘        └────┬────┘        └────┬────┘        │Service   │        └───┬────┘
   │                 │                   │             └────┬─────┘            │
   │  Fill Todo Form │                   │                  │                  │
   ├────────────────>│                   │                  │                