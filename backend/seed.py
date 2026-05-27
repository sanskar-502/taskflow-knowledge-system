"""
Database seed script.

Run this after setting up MySQL to populate the database with:
- Two roles: Admin and User
- A default admin account
- A default user account
- A few sample tasks

Usage:
    cd backend
    python seed.py
"""

from app.database import SessionLocal, engine, Base
from app.models.role import Role
from app.models.user import User
from app.models.task import Task
from app.core.security import hash_password


def seed():
    """Populate the database with initial data for demo and development."""

    # Create all tables first
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # -- Roles --
        admin_role = db.query(Role).filter(Role.role_name == "Admin").first()
        if not admin_role:
            admin_role = Role(role_name="Admin")
            db.add(admin_role)
            db.flush()
            print("Created role: Admin")

        user_role = db.query(Role).filter(Role.role_name == "User").first()
        if not user_role:
            user_role = Role(role_name="User")
            db.add(user_role)
            db.flush()
            print("Created role: User")

        db.commit()

        # -- Users --
        admin_user = db.query(User).filter(User.email == "admin@taskflow.com").first()
        if not admin_user:
            admin_user = User(
                name="Admin",
                email="admin@taskflow.com",
                password_hash=hash_password("admin123"),
                role_id=admin_role.id,
            )
            db.add(admin_user)
            db.flush()
            print("Created admin user: admin@taskflow.com / admin123")

        regular_user = db.query(User).filter(User.email == "user@taskflow.com").first()
        if not regular_user:
            regular_user = User(
                name="John Doe",
                email="user@taskflow.com",
                password_hash=hash_password("user123"),
                role_id=user_role.id,
            )
            db.add(regular_user)
            db.flush()
            print("Created user: user@taskflow.com / user123")

        db.commit()

        # -- Sample Tasks --
        existing_tasks = db.query(Task).count()
        if existing_tasks == 0:
            sample_tasks = [
                Task(
                    title="Review onboarding documentation",
                    description="Go through the company onboarding guide and complete all required steps.",
                    status="Pending",
                    assigned_to=regular_user.id,
                    created_by=admin_user.id,
                ),
                Task(
                    title="Complete compliance training",
                    description="Finish all modules in the annual compliance training program.",
                    status="In Progress",
                    assigned_to=regular_user.id,
                    created_by=admin_user.id,
                ),
                Task(
                    title="Set up development environment",
                    description="Install required tools and configure the local development setup.",
                    status="Completed",
                    assigned_to=regular_user.id,
                    created_by=admin_user.id,
                ),
                Task(
                    title="Upload product knowledge base",
                    description="Gather and upload all product-related documents to the system.",
                    status="Pending",
                    assigned_to=admin_user.id,
                    created_by=admin_user.id,
                ),
                Task(
                    title="Write team introduction post",
                    description="Draft a short introduction about yourself for the team channel.",
                    status="Pending",
                    assigned_to=regular_user.id,
                    created_by=admin_user.id,
                ),
            ]
            db.add_all(sample_tasks)
            db.commit()
            print(f"Created {len(sample_tasks)} sample tasks")

        print("\nSeed completed successfully.")
        print("You can now log in with:")
        print("  Admin: admin@taskflow.com / admin123")
        print("  User:  user@taskflow.com / user123")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
