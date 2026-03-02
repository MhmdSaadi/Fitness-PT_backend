# Fitness-PT-backend


## 🏗️ Tech Stack
- FastAPI
- SQLModel
- PostgreSQL (async)
- Redis
- Docker

## 🚀 Features
- JWT authentication (access/refresh tokens)
- Email verification and password reset
- Async database and Redis
- Modular, extensible structure

## 🛠️ Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd {{project_name}}/HBT_backend
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## 📝 Environment Variables (.env)
```env
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/{{project_name}}_db
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-super-secret-jwt-key  # TODO: Set a secure secret
JWT_ALGORITHM=HS256
SMTP_USERNAME=your-email@example.com   # TODO: Replace with your SMTP username
SMTP_PASSWORD=your-app-password       # TODO: Replace with your SMTP password
APP_NAME={{app_name}}                 # TODO: Replace with your app name
DOMAIN=localhost:3000                 # TODO: Replace with your domain
```

## 🔧 Development
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🗄️ Database Migrations
- Alembic is set up for migrations.
- Example commands:
  ```bash
  docker-compose run --rm alembic revision --autogenerate -m "describe change"
  docker-compose run --rm alembic upgrade head
  ```

## 📚 API Endpoints
- See OpenAPI docs at `/docs` after running the server.

## 📄 License
MIT 
