from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


def seed_admin(db: Session):

    admin = db.query(User).filter(
        User.email == "admin@digitech.com"
    ).first()

    if admin:
        print("✅ Super Admin already exists.")
        return

    admin = User(
        full_name="Super Admin",
        email="admin@digitech.com",
        phone="9876543210",
        password=hash_password("Admin@123"),
        role="SUPER_ADMIN",
        is_active=True
    )

    db.add(admin)
    db.commit()

    print("✅ Super Admin Created Successfully")