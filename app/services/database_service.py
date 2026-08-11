from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.enums import OrganizationType
from app.models.opportunity import Opportunity
from app.models.organization import Organization
from app.models.source import Source


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
                self._update_organization(db, existing, data)
                self._upsert_opportunity(db, existing, data.get("opportunity"))
                self._upsert_sources(db, existing, data.get("fact_sources") or [])
                db.commit()
                db.refresh(existing)
                return existing

            org_type = self._normalize_org_type(
                data.get("organization_type", "")
            )

            industries = data.get("industries") or []
            if isinstance(industries, str):
                industry_value = industries
            else:
                industry_value = ", ".join(
                    str(item) for item in industries if item
                )

            org = Organization(
                name=data.get("organization_name") or website or "Unknown",
                organization_type=OrganizationType(org_type),
                website=website,
                country=self._empty_to_none(data.get("country")),
                city=self._empty_to_none(data.get("city")),
                industry=self._empty_to_none(industry_value),
                description=self._empty_to_none(data.get("summary")),
                email=self._empty_to_none(data.get("email")),
                phone=self._empty_to_none(data.get("phone")),
                linkedin=self._empty_to_none(data.get("linkedin")),
                verification_score=int(
                    data.get("verification_score")
                    or 0
                ),
                verification_status=data.get(
                    "verification_status",
                    "unverified",
                ),
                verification_source=self._empty_to_none(
                    data.get("verification_source")
                ),
            )

            db.add(org)
            db.flush()

            self._upsert_opportunity(db, org, data.get("opportunity"))
            self._upsert_sources(db, org, data.get("fact_sources") or [])

            db.commit()
            db.refresh(org)
            return org

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def _update_organization(self, db: Session, org: Organization, data: dict):
        """Refresh mutable fields on re-research without destroying the row."""

        name = data.get("organization_name")
        if name:
            org.name = name

        org_type = self._normalize_org_type(data.get("organization_type", ""))
        try:
            org.organization_type = OrganizationType(org_type)
        except ValueError:
            pass

        for field, key in (
            ("country", "country"),
            ("city", "city"),
            ("email", "email"),
            ("phone", "phone"),
            ("linkedin", "linkedin"),
            ("description", "summary"),
            ("verification_source", "verification_source"),
        ):
            value = self._empty_to_none(data.get(key))
            if value:
                setattr(org, field, value)

        industries = data.get("industries") or []
        if industries:
            if isinstance(industries, str):
                org.industry = industries
            else:
                org.industry = ", ".join(
                    str(item) for item in industries if item
                )

        if data.get("verification_status"):
            org.verification_status = data["verification_status"]

        if data.get("verification_score") is not None:
            org.verification_score = int(data.get("verification_score") or 0)

        db.add(org)

    def _upsert_opportunity(
        self,
        db: Session,
        org: Organization,
        opportunity: dict | None,
    ):
        if not opportunity or not isinstance(opportunity, dict):
            return

        meaningful = any(
            opportunity.get(key)
            for key in (
                "application_url",
                "eligibility",
                "funding_amount",
                "equity_required",
                "program_duration",
                "deadline",
                "application_process",
                "benefits",
                "startup_stage",
            )
        )
        if not meaningful:
            return

        existing = (
            db.query(Opportunity)
            .filter(Opportunity.organization_id == org.id)
            .first()
        )

        benefits = opportunity.get("benefits") or []
        if isinstance(benefits, str):
            benefits = [benefits] if benefits.strip() else []

        payload = {
            "application_url": self._empty_to_none(
                opportunity.get("application_url")
            ),
            "application_deadline": self._empty_to_none(
                opportunity.get("deadline")
                or opportunity.get("application_deadline")
            ),
            "eligibility": self._empty_to_none(opportunity.get("eligibility")),
            "funding_amount": self._empty_to_none(
                opportunity.get("funding_amount")
            ),
            "funding_currency": self._empty_to_none(
                opportunity.get("funding_currency")
            ),
            "equity_required": self._empty_to_none(
                opportunity.get("equity_required")
            ),
            "program_duration": self._empty_to_none(
                opportunity.get("program_duration")
            ),
            "benefits": benefits or None,
            "application_process": self._empty_to_none(
                opportunity.get("application_process")
            ),
            "startup_stage": self._empty_to_none(
                opportunity.get("startup_stage")
            ),
            "investment_stage": self._stringify(
                opportunity.get("investment_stage")
            ),
            "geographic_focus": self._empty_to_none(
                opportunity.get("geographic_focus")
            ),
            "sector_focus": self._empty_to_none(
                opportunity.get("sector_focus")
            ),
            "program_status": self._empty_to_none(
                opportunity.get("program_status")
            ),
            "mentorship": self._empty_to_none(opportunity.get("mentorship")),
            "investor_access": self._empty_to_none(
                opportunity.get("investor_access")
            ),
            "network_access": self._empty_to_none(
                opportunity.get("network_access")
            ),
            "office_space": self._empty_to_none(
                opportunity.get("office_space")
            ),
            "grants": self._empty_to_none(opportunity.get("grants")),
            "credits": self._empty_to_none(opportunity.get("credits")),
            "cohort_information": self._empty_to_none(
                opportunity.get("cohort_information")
            ),
            "required_documents": self._empty_to_none(
                opportunity.get("required_documents")
            ),
            "selection_process": self._empty_to_none(
                opportunity.get("selection_process")
            ),
        }

        if existing:
            for key, value in payload.items():
                if value is not None:
                    setattr(existing, key, value)
            db.add(existing)
        else:
            db.add(Opportunity(organization_id=org.id, **payload))

    def _upsert_sources(
        self,
        db: Session,
        org: Organization,
        fact_sources: list,
    ):
        if not fact_sources:
            return

        for fact in fact_sources:
            if not isinstance(fact, dict):
                continue

            url = fact.get("source_url") or fact.get("url")
            if not url:
                continue

            field_name = fact.get("field") or fact.get("field_name")
            value = fact.get("value")
            source_type = fact.get("source_type") or "official"
            verified = bool(fact.get("verified"))

            existing = (
                db.query(Source)
                .filter(
                    Source.organization_id == org.id,
                    Source.url == url,
                    Source.field_name == field_name,
                )
                .first()
            )

            if existing:
                if value:
                    existing.value = str(value)
                existing.source_type = source_type
                existing.verified = verified
                db.add(existing)
            else:
                db.add(
                    Source(
                        organization_id=org.id,
                        url=url,
                        source_type=source_type,
                        field_name=field_name,
                        value=str(value) if value is not None else None,
                        verified=verified,
                    )
                )

    def _normalize_org_type(self, org_type: str | None) -> str:
        value = (org_type or "").strip().lower()
        aliases = {
            "angel": OrganizationType.INVESTOR.value,
            "vc": OrganizationType.INVESTOR.value,
            "venture capital": OrganizationType.INVESTOR.value,
            "funding": OrganizationType.GRANT.value,
            "programme": OrganizationType.PROGRAM.value,
        }
        value = aliases.get(value, value)
        allowed = {item.value for item in OrganizationType}
        if value not in allowed:
            return OrganizationType.STARTUP.value
        return value

    @staticmethod
    def _empty_to_none(value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @staticmethod
    def _stringify(value):
        if value is None:
            return None
        if isinstance(value, list):
            joined = ", ".join(str(item) for item in value if item)
            return joined or None
        text = str(value).strip()
        return text or None
