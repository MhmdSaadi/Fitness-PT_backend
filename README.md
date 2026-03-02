
# Fitness-PT-backend

## 🎯 What Problem It Solves

Performance enhancement coaches often struggle to scale their business while maintaining a high level of professional oversight. Managing multiple clients via spreadsheets or messaging apps leads to fragmented data and missed progress tracking.

This platform provides a **professional, centralized system** for coaches to:

* **Streamline Onboarding:** Automated registration and email verification.
* **Client Management:** A dedicated backend to track and follow client progress securely.
* **Performance Scaling:** High-performance architecture (FastAPI + Redis) designed to handle a growing client base without lag.
* **Professional Branding:** A robust API that serves as the foundation for a high-end, bespoke coaching experience.

## 🏗️ Tech Stack

* **FastAPI**: High-performance web framework.
* **SQLModel**: Interaction with databases using Python objects.
* **PostgreSQL (async)**: Reliable relational data storage.
* **Redis**: Fast caching and session management.
* **Docker**: Containerized environment for consistent deployment.

## 🚀 Features

* JWT authentication (access/refresh tokens)
* Email verification and password reset
* Async database and Redis integration
* Modular, extensible structure for adding coaching-specific modules

## 🛠️ Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd Fitness-PT-backend/HBT_backend

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
* API: http://localhost:8000
* Docs: http://localhost:8000/docs



## 📝 Environment Variables (.env)

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/fitness_pt_db
REDIS_URL=redis://redis:6379/0
JWT_SECRET=your-super-secret-jwt-key 
JWT_ALGORITHM=HS256
SMTP_USERNAME=your-email@example.com 
SMTP_PASSWORD=your-app-password 
APP_NAME=FitnessPT_Performance
DOMAIN=localhost:3000

```

## 🔧 Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

```

## 🗄️ Database Migrations

* Alembic is set up for migrations.
* Example commands:
```bash
docker-compose run --rm alembic revision --autogenerate -m "initial migration"
docker-compose run --rm alembic upgrade head

```



## 📚 API Endpoints

* See OpenAPI docs at `/docs` after running the server.

## 📄 License

MIT



