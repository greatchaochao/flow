"""
Seed database with test data.
"""

from datetime import datetime, timedelta
from app.database.connection import SessionLocal
from app.database.models import User, Company
from app.utils.security import hash_password


def seed_database():
    """Seed database with initial test data."""
    db = SessionLocal()

    try:
        print("Seeding database...")

        # Create test company
        company = Company(
            company_name="UK SMB Trading Ltd",
            registered_country="GB",
            industry_sector="Import/Export",
            fx_volume_band="medium",
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"✓ Created company: {company.company_name}")

        # Create test users
        users_data = [
            {
                "email": "admin@uksmb.com",
                "password": "admin123",
                "full_name": "Admin User",
                "role": "admin",
            },
            {
                "email": "maker@uksmb.com",
                "password": "maker123",
                "full_name": "Maker User",
                "role": "maker",
            },
            {
                "email": "approver@uksmb.com",
                "password": "approver123",
                "full_name": "Approver User",
                "role": "approver",
            },
        ]

        for user_data in users_data:
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                company_id=company.id,
                is_active=True,
            )
            db.add(user)
            print(f"✓ Created user: {user.email} (password: {user_data['password']})")

        db.commit()
        print("\n✓ Database seeded successfully!")
        print("\nTest Credentials:")
        print("=" * 50)
        for user_data in users_data:
            print(
                f"Role: {user_data['role']:10} | Email: {user_data['email']:20} | Password: {user_data['password']}"
            )

    except Exception as e:
        print(f"✗ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
