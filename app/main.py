from fastapi import FastAPI
from app import models
from app.database import engine
from app.routers import auth, records, analytics, users

# 1. The Spark: This automatically generates our schema (Users, Records, etc.)
# right inside the postgresql container on startup.
models.Base.metadata.create_all(bind=engine)

# 2. Documentation: Defining the new Documentation Metadata for our Tags
tags_metadata = [
    {
        "name": "Authentication",
        "description": "Operations to register users and securely issue stateless **JWT Bearer Tokens**. Features timing-attack mitigation on login.",
    },
    {
        "name": "User Management",
        "description": "Admin-only routes to manage user roles and perform **soft-deletes** (deactivation) for audit compliance.",
    },
    {
        "name": "Financial Records",
        "description": "Core CRUD operations for the financial ledger. Includes a dynamic search engine with multi-parameter filtering.",
    },
    {
        "name": "Analytics Dashboard",
        "description": "High-performance, database-level SQL aggregations for real-time financial metrics and outlier detection.",
    },
]

# 3. The Engine: Initializing the FastAPI Application
app = FastAPI(
    title="Fintech Ledger API",
    description="A simple concurrent Fintech Records Manager with PostgreSQL",
    version="1.1.0",
    openapi_tags=tags_metadata,
)

# 4. Plugging the Routers into the Application
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(analytics.router)

# 5. A quick health check route to check how the server is doing
@app.get("/")
def read_root():
    return {"status": "Fintech Ledger API Vault is Online & Healthy!"}