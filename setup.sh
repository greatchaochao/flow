#!/bin/bash

# Flow Platform - Database Setup Script
# Sets up PostgreSQL database with schema and seed data

set -e  # Exit on error

echo "=============================="
echo "Flow Platform - Database Setup"
echo "=============================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Start PostgreSQL
echo "1️⃣  Starting PostgreSQL database..."
docker compose up -d postgres
echo ""

# Wait for PostgreSQL to be ready
echo "2️⃣  Waiting for PostgreSQL to be ready..."
sleep 5

# Check if database is ready
until docker compose exec -T postgres pg_isready -U flow_user -d flow_db > /dev/null 2>&1; do
    echo "   Waiting for database..."
    sleep 2
done

echo "✓ PostgreSQL is ready"
echo ""

# Run database migrations
echo "3️⃣  Creating database schema..."
alembic upgrade head 2>/dev/null || {
    echo "   No migrations found. Creating initial migration..."
    alembic revision --autogenerate -m "Initial database schema"
    alembic upgrade head
}
echo "✓ Database schema created"
echo ""

# Seed test data
echo "4️⃣  Seeding test data..."
python scripts/seed_data.py
echo "✓ Test data seeded"
echo ""

echo "=============================="
echo "✅ Database Setup Complete!"
echo "=============================="
echo ""
echo "Database Info:"
echo "  Host: localhost:5432"
echo "  Database: flow_db"
echo "  User: flow_user"
echo "  Password: flow_password"
echo ""
echo "Demo Users:"
echo "  Admin: admin@uksmb.com / admin123"
echo "  Maker: maker@uksmb.com / maker123"
echo "  Approver: approver@uksmb.com / approver123"
echo ""
echo "Next steps:"
echo "  1. Run: streamlit run main.py"
echo "  2. Open http://localhost:8501"
echo "  3. Login with demo credentials"
echo ""
echo "To stop the database: docker compose down"
echo "To view logs: docker compose logs -f postgres"
echo ""
