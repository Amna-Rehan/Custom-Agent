from sqlalchemy.orm import Session

from app.database.session import SessionLocal

from app.models.organization import Organization
from app.models.enums import OrganizationType


class DatabaseService:

    def save(self, data: dict):

        db: Session = SessionLocal()

        try:
            website = data.get("website")
            existing = (
                db.query(Organization)
                .filter(Organization.website == website)
                .first()
            )

            if existing:
                print(f"{website} already exists.")
                return existing
            org_type = data.get("organization_type", "").strip().lower()

            if org_type not in [e.value for e in OrganizationType]:
              org_type = OrganizationType.STARTUP.value

            org = Organization(
               name=data.get("organization_name"),
               organization_type=OrganizationType(org_type),
               website=data.get("website"),
               country=data.get("country"),
               city=data.get("city"),
               industry=", ".join(data.get("industries", [])),
               description=data.get("summary"),
               email=data.get("email"),
               phone=data.get("phone"),
               linkedin=data.get("linkedin"),
               verification_score=data.get("confidence_score", 0),
            )

            db.add(org)

            db.commit()

            db.refresh(org)

            return org

        finally:

            db.close()