# 🧠 TaskFlow AI — Intelligent Task & Knowledge Management System

<div align="center">
  <h3>An AI-powered platform demonstrating systems engineering, not just API wrapping.</h3>
</div>

---

## 🏗️ Architecture & System Design

TaskFlow AI is built using a modern, scalable, and modular layered architecture. It cleanly separates concerns to ensure maintainability and testability.

### High-Level System Flow
```mermaid
graph TD
    Client[React Frontend] <-->|REST API (JSON)| FastAPI[FastAPI Backend]
    FastAPI <-->|SQLAlchemy ORM| MySQL[(MySQL Database)]
    FastAPI <-->|AI Pipeline| ChromaDB[(ChromaDB Vector Store)]
    FastAPI -->|Middleware| Logging(Activity Logger)
```

### Backend Layered Architecture (FastAPI)
The backend avoids the "fat controller" anti-pattern by strictly adhering to a layered design:

1. **API Routers (`/app/api`)**: Thin controllers. They only handle HTTP request parsing, input validation (via Pydantic), and returning responses. 
2. **Services (`/app/services`)**: The core business logic. This is where authentication rules, task filtering, and document processing live.
3. **Data Access / ORM (`/app/models` & `/app/database`)**: SQLAlchemy models mapping to the MySQL schema. 
4. **Cross-Cutting Concerns (`/app/core`)**: Security (JWT, hashing), dependencies (RBAC), and middleware (Activity Logging).
5. **AI Module (`/app/ai`)**: Encapsulates the entire embedding and vector search pipeline.

---

## 🤖 Core AI Implementation (No External APIs)

A key constraint of the assignment was to **implement the core AI logic** without relying solely on external LLM wrappers (like OpenAI). TaskFlow accomplishes this via a fully localized embedding and retrieval pipeline.

### 1. Document Processing & Chunking
When a user uploads a `.txt` file, feeding the entire document into an embedding model degrades semantic accuracy.
* **Intelligent Chunking**: The system splits text into ~500-character chunks.
* **Overlap Strategy**: We use a 50-character overlap between chunks. This prevents losing critical context if a relevant sentence falls exactly on a chunk boundary.

### 2. Local Embeddings (`sentence-transformers`)
* We use `all-MiniLM-L6-v2` loaded locally.
* It converts text chunks into 384-dimensional dense vector embeddings.
* It runs entirely on the host machine (CPU compatible), ensuring data privacy and zero API latency/costs.

### 3. Vector Database (`ChromaDB`)
* Embeddings are stored persistently in ChromaDB (`/chroma_data`).
* Queries are converted to embeddings using the same model, and we use **Cosine Similarity** to retrieve the most semantically relevant chunks.
* Results are returned with an exact `relevance_score` to the user.

---

## ✨ Key Features

* **JWT & Role-Based Access Control (RBAC)**: Secure authentication with Admin and User roles enforced at the router level via FastAPI dependency injection.
* **Semantic Knowledge Search**: Natural language search over uploaded documents using the local AI pipeline.
* **Task Management**: Admins create and assign tasks. Users update statuses. Robust API filtering (e.g., `?status=Completed&assigned_to=1`).
* **Automated Activity Logging**: A custom FastAPI middleware intercepts every request and automatically logs actions (Login, Upload, Search, Task Update) to the database.
* **Analytics Dashboard**: Aggregated metrics combining relational data (tasks) and vector data (document chunks), alongside a feed of recent activity and popular search queries.
* **Premium UI/UX**: Built with React, Zustand, and custom CSS featuring a modern glassmorphic aesthetic, status badges, and relevance-score progress bars.

---

## 🗄️ Database Schema

The database strictly follows relational design principles (3NF) with appropriate foreign keys and cascading rules.

* **`roles`**: Defines `Admin` and `User`.
* **`users`**: Contains authenticated users (`password_hash`, `role_id` -> FK to roles).
* **`tasks`**: Uses an `ENUM` for status (Pending, In Progress, Completed). Has two FKs to users (`assigned_to`, `created_by`).
* **`documents`**: Tracks uploaded files, paths, and importantly, `chunk_count` to monitor the AI pipeline's processing status.
* **`activity_logs`**: Uses a `JSON` column for `details` to store flexible payloads (like search query text) alongside the `action` type.

---

## 🛠️ Setup & Installation

We provide two ways to run the application. **Docker is highly recommended** as it spins up the database, backend, and frontend automatically.

### Option 1: Docker Compose (Recommended)

1. Ensure you have Docker and Docker Compose installed.
2. In the project root directory, run:
   ```bash
   docker-compose up --build
   ```
3. In a new terminal, seed the database with initial users and tasks:
   ```bash
   docker exec -it taskflow_backend python seed.py
   ```
4. Access the app:
   - Frontend UI: `http://localhost:5173`
   - Backend API Docs (Swagger): `http://localhost:8000/docs`

### Option 2: Manual Setup

**1. Database**
Ensure MySQL 8.0 is running locally and create a database named `taskflow_db`.

**2. Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # (or venv\Scripts\activate on Windows)
pip install -r requirements.txt
cp .env.example .env      # Update DB credentials inside if needed
python seed.py            # Seed the database
uvicorn app.main:app --reload
```

**3. Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## 📡 Core APIs

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| `POST` | `/api/auth/login` | Public | Returns JWT access token. |
| `POST` | `/api/tasks` | Admin | Creates and assigns a task. |
| `GET`  | `/api/tasks` | Both | Lists tasks. Supports dynamic filters: `?status=...&assigned_to=...&page=1&sort_by=created_at` |
| `PATCH`| `/api/tasks/{id}` | Both | Updates task status (users can only update their assigned tasks). |
| `POST` | `/api/documents` | Admin | Uploads a `.txt` file, chunks it, embeds it, and stores in Vector DB. |
| `GET`  | `/api/search` | Both | Semantic search query. Ex: `?q=how do i request time off&top_k=5` |
| `GET`  | `/api/analytics` | Admin | Aggregated stats for the dashboard. |

---

## ✅ Evaluation Criteria Checklist

Here is how this implementation fulfills the assignment's mandate:

1. **Authentication & RBAC**: Uses PyJWT. Routes are protected via FastAPI Dependency Injection (`get_current_user`, `require_role("Admin")`).
2. **Database (MySQL)**: 5 core tables properly normalized. SQLAlchemy used for safe ORM interaction.
3. **Document Upload**: Processes `.txt` files, saves to disk, logs metadata in DB.
4. **AI Feature**: No LLM API calls. Core logic is implemented locally using `sentence-transformers` for embeddings and `ChromaDB` for the vector store. Uses an overlapping chunking strategy.
5. **Task Management**: Full CRUD. Admins create/assign; Users update status.
6. **Dynamic Filtering**: The `GET /api/tasks` endpoint supports complex filtering, sorting, and pagination via query parameters.
7. **Activity Logging**: Implemented cleanly as a global FastAPI middleware, eliminating repetitive code in route handlers.
8. **Basic Analytics**: The `/api/analytics` endpoint joins multiple tables to provide a comprehensive dashboard (total tasks, completion rates, KB size, top search queries).
