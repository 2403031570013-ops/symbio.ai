import logging
from datetime import datetime, timedelta, timezone
import base64
import hashlib
import hmac
import secrets

from sqlalchemy.orm import Session
from sqlalchemy import inspect, text

from app.db.session import Base, engine, SessionLocal
from app.models import (
    Factory, Material, Transaction, Match, Analytics, User,
    AIRecommendation, DemandPrediction, PriceForecast,
    CarbonFootprint, ESGScore, SustainabilityDashboard,
    WasteImpact, GreenCertification, CarbonCredit,
    RouteOptimization, Inventory, SupplyChainVisibility,
    ShipmentTracking, SupplierPerformance, LogisticsCost,
    ComplianceCheck, RiskAssessment, AuditTrail,
    DocumentCompliance, RegulatoryUpdate, FraudDetection,
    DynamicPricing, SmartNotification, WorkflowAutomation,
    Contract, Payment, BusinessIntelligence, AnomalyDetection, PredictiveMaintenance,
    RefreshToken, EmailOtp
)
from app.models.user import UserRole

logger = logging.getLogger("symbioai.db")


def ensure_sqlite_columns() -> None:
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    existing = {table: {column["name"] for column in inspector.get_columns(table)} for table in inspector.get_table_names()}
    additions = {
        "users": {
            "email_verified": "BOOLEAN DEFAULT 0",
            "email_verification_token": "VARCHAR",
            "password_reset_token": "VARCHAR",
            "two_factor_enabled": "BOOLEAN DEFAULT 0",
            "two_factor_secret": "VARCHAR",
            "recovery_codes": "TEXT",
            "trusted_device_token": "VARCHAR",
            "profile_image_url": "VARCHAR",
            "factory_logo_url": "VARCHAR",
        },
        "materials": {
            "certificate_url": "VARCHAR",
            "photo_url": "VARCHAR",
            "lab_report_url": "VARCHAR",
            "storage_provider": "VARCHAR",
        },
    }
    with engine.begin() as connection:
        for table, columns in additions.items():
            if table not in existing:
                continue
            for column, ddl in columns.items():
                if column not in existing[table]:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16).encode()
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return base64.b64encode(salt + derived).decode()


def seed_database(db: Session) -> None:
    # ---- Users ----
    if db.query(User).count() == 0:
        logger.info("Seeding users...")
        db.add_all([
            User(id="user-qa-id", email="qa+sandbox@symbioai.io", full_name="QA User",
                 hashed_password=_hash_password("Password123!"), role=UserRole.WASTE_PRODUCER, is_active=True),
            User(id="user-admin-id", email="admin@symbioai.com", full_name="Super Admin",
                 hashed_password=_hash_password("Admin@123"), role=UserRole.SUPER_ADMIN, is_active=True),
            User(id="user-manager-id", email="manager@symbioai.com", full_name="Operations Admin",
                 hashed_password=_hash_password("Manager@123"), role=UserRole.ADMIN, is_active=True),
            User(id="user-producer-id", email="producer@symbioai.io", full_name="BioTech Refineries",
                 hashed_password=_hash_password("Password123!"), role=UserRole.WASTE_PRODUCER, is_active=True),
        ])
        db.commit()

    admin = db.query(User).filter(User.email == "admin@symbioai.com").first()
    if not admin:
        db.add(User(id="user-admin-production-id", email="admin@symbioai.com", full_name="Super Admin",
                    hashed_password=_hash_password("Admin@123"), role=UserRole.SUPER_ADMIN, is_active=True))
        db.commit()
    elif admin.role != UserRole.SUPER_ADMIN:
        admin.role = UserRole.SUPER_ADMIN
        db.commit()

    manager = db.query(User).filter(User.email == "manager@symbioai.com").first()
    if not manager:
        db.add(User(id="user-manager-production-id", email="manager@symbioai.com", full_name="Operations Admin",
                    hashed_password=_hash_password("Manager@123"), role=UserRole.ADMIN, is_active=True))
        db.commit()

    qa = db.query(User).filter(User.email == "qa+sandbox@symbioai.io").first()
    uid = qa.id if qa else "user-qa-id"

    # ---- Factories ----
    if db.query(Factory).count() == 0:
        logger.info("Seeding factories...")
        db.add_all([
            Factory(id="factory-id", name="Symbio Chemical Processing Plant 1",
                    industry="Chemicals", location="Houston, TX, USA", verified=True, owner_id=uid),
            Factory(id="factory-2", name="Bio-Organic Waste Solutions",
                    industry="Agriculture", location="Chicago, IL, USA", verified=True, owner_id=uid),
        ])
        db.commit()

    # ---- Materials ----
    if db.query(Material).count() == 0:
        logger.info("Seeding materials...")
        db.add_all([
            Material(id="material-id", name="Industrial Acetic Acid Waste",
                     chemical_composition="C2H4O2 85pct Water 15pct", physical_state="Liquid",
                     quantity="5000L", frequency="Weekly", certificate="ISO 9001",
                     owner_id=uid, status="approved"),
            Material(id="material-2", name="Fly Ash",
                     chemical_composition="SiO2 60pct Al2O3 25pct Fe2O3 10pct", physical_state="Solid Powder",
                     quantity="12000kg", frequency="Monthly", certificate="EPA FlyAsh-Cert",
                     owner_id=uid, status="approved"),
        ])
        db.commit()

    # ---- Matches ----
    if db.query(Match).count() == 0:
        logger.info("Seeding matches...")
        db.add_all([
            Match(id="match-1", material_id="material-id", partner_name="DuPont Polymer Labs",
                  symbio_score=94, distance_km=14.5, carbon_savings="1,240 kg CO2e/month",
                  summary="DuPont polymer synthesis can consume acetic acid waste as neutralization reagent."),
            Match(id="match-2", material_id="material-2", partner_name="Apex Concrete Producers",
                  symbio_score=88, distance_km=42.1, carbon_savings="3,450 kg CO2e/month",
                  summary="Apex concrete mixes use fly ash as partial replacement for Portland cement."),
        ])
        db.commit()

    # ---- Transactions ----
    if db.query(Transaction).count() == 0:
        logger.info("Seeding transactions...")
        db.add_all([
            Transaction(id="tx-1", material_id="material-id", partner_name="DuPont Polymer Labs",
                        amount=3400.0, status="In Transit"),
            Transaction(id="tx-2", material_id="material-2", partner_name="Apex Concrete Producers",
                        amount=8950.0, status="Completed"),
        ])
        db.commit()

    # ---- Analytics ----
    if db.query(Analytics).count() == 0:
        logger.info("Seeding analytics...")
        db.add(Analytics(id="analytics-default", revenue_generated=12450.0, co2_avoided=4690.0,
                         landfill_diversion=17000.0, active_matches=2.0))
        db.commit()

    # ---- AI Recommendations ----
    if db.query(AIRecommendation).count() == 0:
        logger.info("Seeding AI recommendations...")
        db.add_all([
            AIRecommendation(id="rec-1", user_id=uid, recommendation_type="material",
                title="Divert Acetic Acid to DuPont Labs",
                description="Our matchmaking engine found DuPont Polymer Labs has a compatible chemistry requirement. Route this material for cost savings and Scope 3 emission reductions.",
                confidence_score=0.94, expected_benefit={"cost_savings": 2300, "carbon_reduction_kg": 1240},
                status="pending", custom_metadata={"match_id": "match-1"}),
            AIRecommendation(id="rec-2", user_id=uid, recommendation_type="pricing",
                title="Increase Fly Ash Pricing by 8pct",
                description="Market analysis shows regional shortage of cement substitutes. Adjust base price from 75 per ton to 81 per ton to maximize profitability.",
                confidence_score=0.88, expected_benefit={"revenue_uplift": 960, "market_demand_percentile": 92},
                status="pending", custom_metadata={}),
            AIRecommendation(id="rec-3", user_id=uid, recommendation_type="route",
                title="Switch Fly Ash Logistics to Intermodal Rail",
                description="Switching 60pct of transport volume from road to rail will reduce CO2 output by 45pct and decrease logistics spend.",
                confidence_score=0.91, expected_benefit={"cost_savings": 1400, "co2_savings_kg": 850},
                status="pending", custom_metadata={}),
        ])
        db.commit()

    # ---- Demand Predictions ----
    if db.query(DemandPrediction).count() == 0:
        db.add(DemandPrediction(id="dp-1", material_id="material-id", prediction_period="monthly",
            predicted_demand=6200.0, confidence_interval={"lower": 5800.0, "upper": 6600.0},
            factors={"seasonality": 0.15, "industrial_activity": 0.85},
            model_version="symbio-demand-v2.1", accuracy_score=0.93,
            prediction_date=datetime.now(timezone.utc)))
        db.commit()

    # ---- Price Forecasts ----
    if db.query(PriceForecast).count() == 0:
        db.add(PriceForecast(id="pf-1", material_id="material-id", forecast_period="monthly",
            current_price=85.0, predicted_price=94.2, price_change_percent=10.8,
            trend="increasing", volatility=0.12, confidence_score=0.89,
            market_factors={"raw_materials_shortage": 0.4, "regulatory_incentives": 0.6},
            target_date=datetime.now(timezone.utc) + timedelta(days=30)))
        db.commit()

    # ---- Carbon Footprints ----
    if db.query(CarbonFootprint).count() == 0:
        now = datetime.now(timezone.utc)
        db.add(CarbonFootprint(id="cf-1", factory_id="factory-id", material_id="material-id",
            emission_source="production", co2_emitted=3450.0, baseline_co2=3900.0,
            reduction_percentage=11.5, calculation_method="ISO 14064-1", verified=True,
            verification_date=now - timedelta(days=5),
            period_start=now - timedelta(days=30), period_end=now))
        db.commit()

    # ---- ESG Scores ----
    if db.query(ESGScore).count() == 0:
        now = datetime.now(timezone.utc)
        db.add(ESGScore(id="esg-1", factory_id="factory-id",
            environmental_score=87.5, social_score=82.0, governance_score=91.0, overall_score=86.8,
            rating="AA", assessment_date=now - timedelta(days=15),
            next_assessment_date=now + timedelta(days=350),
            criteria={"waste_recycling": 92, "water_neutrality": 78, "worker_safety": 85},
            improvements={"suggestions": ["Install roof solar panels", "Expand localized wastewater recovery"]}))
        db.commit()

    # ---- Sustainability Dashboards ----
    if db.query(SustainabilityDashboard).count() == 0:
        now = datetime.now(timezone.utc)
        db.add(SustainabilityDashboard(id="sd-1", factory_id="factory-id",
            total_waste_diverted=17000.0, total_co2_saved=4690.0, water_saved=450000.0,
            energy_saved=24500.0, recycling_rate=78.5, circular_economy_score=86.0,
            zero_waste_certified=True,
            green_certifications={"ISO 14001": "Verified", "LEED Gold": "Active"},
            period_start=now - timedelta(days=180), period_end=now))
        db.commit()

    # ---- Waste Impacts ----
    if db.query(WasteImpact).count() == 0:
        db.add(WasteImpact(id="wi-1", material_id="material-id", waste_type="corrosive_liquid",
            environmental_impact={"ph_level": 2.5, "biodegradability": "low"},
            economic_value=3.40, diversion_method="recycling", impact_score=75.0))
        db.commit()

    # ---- Green Certifications ----
    if db.query(GreenCertification).count() == 0:
        now = datetime.now(timezone.utc)
        db.add(GreenCertification(id="gc-1", factory_id="factory-id",
            certification_name="ISO 14001:2015", certification_body="SGS Global Services",
            certification_level="Certified",
            issue_date=now - timedelta(days=200), expiry_date=now + timedelta(days=500),
            status="active", audit_score=94.5,
            requirements={"audit_frequency": "annual", "corrective_actions_pending": 0}))
        db.commit()

    # ---- Carbon Credits ----
    if db.query(CarbonCredit).count() == 0:
        db.add(CarbonCredit(id="cc-1", factory_id="factory-id",
            credit_amount=150.0, credit_type="avoidance", project_type="Industrial Waste Symbiosis",
            verification_status="verified", price_per_credit=18.50, total_value=2775.0,
            available_for_sale=True, vintage_year=2025, registry="Verra VCS"))
        db.commit()

    # ---- Route Optimizations ----
    if db.query(RouteOptimization).count() == 0:
        db.add(RouteOptimization(id="ro-1", shipment_id="ship-1",
            origin="Houston, TX", destination="Dallas, TX",
            original_distance=385.0, optimized_distance=362.0, distance_saved=23.0,
            original_time=4.5, optimized_time=4.1, time_saved=0.4,
            original_cost=580.0, optimized_cost=510.0, cost_saved=70.0, co2_saved=85.5,
            route_coordinates={"waypoints": ["Houston", "Conroe", "Huntsville", "Corsicana", "Dallas"]},
            optimization_algorithm="Dijkstra Neural Optimizer v3"))
        db.commit()

    # ---- Inventories ----
    if db.query(Inventory).count() == 0:
        now = datetime.now(timezone.utc)
        db.add_all([
            Inventory(id="inv-1", factory_id="factory-id", material_id="material-id",
                current_stock=1500.0, minimum_stock=500.0, maximum_stock=5000.0,
                reorder_point=800.0, reorder_quantity=2000.0, stock_status="normal",
                last_restock_date=now - timedelta(days=10), next_restock_date=now + timedelta(days=20),
                turnover_rate=4.2, holding_cost=150.0, stockout_count=0),
            Inventory(id="inv-2", factory_id="factory-id", material_id="material-2",
                current_stock=350.0, minimum_stock=400.0, maximum_stock=3000.0,
                reorder_point=600.0, reorder_quantity=1500.0, stock_status="low",
                last_restock_date=now - timedelta(days=28), next_restock_date=now + timedelta(days=2),
                turnover_rate=6.1, holding_cost=95.0, stockout_count=1),
        ])
        db.commit()

    # ---- Supply Chain Visibility ----
    if db.query(SupplyChainVisibility).count() == 0:
        db.add(SupplyChainVisibility(id="scv-1", material_id="material-id",
            supply_chain_stage="manufacturing", supplier_id="factory-2",
            location="Chicago, IL", status="active",
            estimated_arrival=datetime.now(timezone.utc) + timedelta(days=4),
            risk_level="low", tracking_number="TRK-982457812"))
        db.commit()

    # ---- Shipment Tracking ----
    if db.query(ShipmentTracking).count() == 0:
        db.add(ShipmentTracking(id="st-1", shipment_id="ship-1",
            current_location="Huntsville, TX", destination="Dallas, TX", status="in_transit",
            estimated_delivery=datetime.now(timezone.utc) + timedelta(hours=3),
            carrier="EcoFreight Logistics",
            tracking_events=[{"time": "10:00 AM", "event": "Departed Houston Depot"},
                             {"time": "12:15 PM", "event": "Arrived Huntsville Weigh Station"}],
            temperature={"current": 22.4, "status": "nominal"},
            humidity={"current": 45.2, "status": "nominal"}, condition="good"))
        db.commit()

    # ---- Supplier Performance ----
    if db.query(SupplierPerformance).count() == 0:
        db.add(SupplierPerformance(id="sp-1", supplier_id="factory-2", factory_id="factory-id",
            on_time_delivery_rate=96.5, quality_score=98.0, response_time=2.4,
            price_competitiveness=88.5, communication_score=95.0, overall_score=94.8,
            rating="excellent", total_orders=48, total_deliveries=47, delayed_deliveries=1,
            quality_issues=0, assessment_period="Q2-2026"))
        db.commit()

    # ---- Logistics Costs ----
    if db.query(LogisticsCost).count() == 0:
        db.add(LogisticsCost(id="lc-1", shipment_id="ship-1", cost_category="transportation",
            base_cost=420.0, fuel_surcharge=60.0, handling_fee=30.0, insurance_cost=20.0,
            total_cost=530.0, cost_per_unit=0.11, cost_per_km=1.38,
            budget=600.0, variance=-70.0, variance_percentage=-11.6))
        db.commit()

    # ---- Compliance Checks ----
    if db.query(ComplianceCheck).count() == 0:
        now = datetime.now(timezone.utc)
        db.add_all([
            ComplianceCheck(id="cck-1", factory_id="factory-id",
                check_type="environmental", regulation="EPA RCRA Corrosive Waste Guidelines",
                jurisdiction="Texas, USA", status="compliant", compliance_score=100.0,
                last_audit_date=now - timedelta(days=45), next_audit_date=now + timedelta(days=320),
                findings=[{"issue": "none", "severity": "low"}], corrective_actions=[], priority="medium"),
            ComplianceCheck(id="cck-2", factory_id="factory-id",
                check_type="safety", regulation="OSHA Chemical Storage Standard 1910.106",
                jurisdiction="Federal, USA", status="pending", compliance_score=85.0,
                last_audit_date=now - timedelta(days=90), next_audit_date=now + timedelta(days=5),
                findings=[{"issue": "Secondary containment labeling faded", "severity": "low"}],
                corrective_actions=[{"action": "Repaint container warning labels", "deadline": "2026-07-15"}],
                priority="high", deadline=now + timedelta(days=10)),
        ])
        db.commit()

    # ---- Risk Assessments ----
    if db.query(RiskAssessment).count() == 0:
        db.add(RiskAssessment(id="ra-1", factory_id="factory-id",
            risk_category="environmental",
            risk_description="Chemical leak from primary storage vessel due to high temperature expansion.",
            likelihood=2, impact=4, risk_score=8.0, risk_level="medium",
            mitigation_strategies=[{"plan": "Install automatic pressure release valve and thermal backup coolant jacket."}],
            owner="John Doe (Safety Director)", status="open", residual_risk=3.0))
        db.commit()

    # ---- Audit Trails ----
    if db.query(AuditTrail).count() == 0:
        db.add(AuditTrail(id="at-1", entity_type="material", entity_id="material-id",
            action="create", user_id=uid, user_role="Waste Producer",
            changes={"name": "Industrial Acetic Acid Waste", "quantity": "5000L"}))
        db.commit()

    # ---- Document Compliance ----
    if db.query(DocumentCompliance).count() == 0:
        now = datetime.now(timezone.utc)
        db.add(DocumentCompliance(id="dc-1", factory_id="factory-id",
            document_type="Permit", document_name="RCRA Hazardous Waste Storage License",
            document_number="TXD980749811",
            issuing_authority="Texas Commission on Environmental Quality",
            issue_date=now - timedelta(days=300), expiry_date=now + timedelta(days=65),
            status="active", reminder_days=30))
        db.commit()

    # ---- Regulatory Updates ----
    if db.query(RegulatoryUpdate).count() == 0:
        now = datetime.now(timezone.utc)
        db.add(RegulatoryUpdate(id="ru-1",
            regulation_name="EPA Circular Economy and Waste Substitution Act",
            jurisdiction="Federal, USA",
            effective_date=now + timedelta(days=90),
            compliance_deadline=now + timedelta(days=180),
            description="New federal incentives and compliance frameworks regarding reuse of industrial byproducts as chemical raw materials.",
            impact_level="high",
            affected_industries=["Chemical Manufacturing", "Building Construction"],
            requirements=["Mandatory registration of all byproducts traded", "Purity audits every 180 days"]))
        db.commit()

    # ---- Fraud Detections ----
    if db.query(FraudDetection).count() == 0:
        db.add(FraudDetection(id="fd-1", entity_type="factory", entity_id="factory-id",
            detection_type="price_manipulation", risk_score=14.5, confidence=95.0,
            indicators=["Pricing aligned within normal 5pct standard deviation"],
            status="flagged",
            investigation_notes="Automated review: listing price verified within reasonable limits."))
        db.commit()

    # ---- Dynamic Pricing ----
    if db.query(DynamicPricing).count() == 0:
        db.add(DynamicPricing(id="dpri-1", material_id="material-id",
            base_price=85.0, current_price=94.2, price_change=9.2,
            demand_factor=1.25, supply_factor=0.92,
            algorithm="Demand-Supply Elasticity Matrix v1", confidence_score=92.5))
        db.commit()

    # ---- Smart Notifications ----
    if db.query(SmartNotification).count() == 0:
        db.add_all([
            SmartNotification(id="sn-1", user_id=uid, notification_type="match",
                title="High Confidence Match Ready!",
                message="New match found between your Acetic Acid waste and DuPont Polymer Labs (Score: 94).",
                priority="high", status="unread", action_required=True, action_url="/matches"),
            SmartNotification(id="sn-2", user_id=uid, notification_type="compliance",
                title="OSHA Audit Looming",
                message="Safety storage compliance check is pending and due in 5 days.",
                priority="urgent", status="unread", action_required=True, action_url="/compliance"),
        ])
        db.commit()

    # ---- Workflow Automations ----
    if db.query(WorkflowAutomation).count() == 0:
        db.add(WorkflowAutomation(id="wa-1", name="Auto-Match Material Additions",
            description="Trigger match engine immediately upon registering new factory waste.",
            trigger_type="material_added",
            trigger_conditions={"min_quantity_liters": 1000},
            actions=[{"action": "run_matcher", "parameters": {"confidence_threshold": 0.8}}],
            enabled=True, created_by=uid))
        db.commit()

    # ---- Contracts ----
    if db.query(Contract).count() == 0:
        now = datetime.now(timezone.utc)
        db.add(Contract(id="con-1", contract_number="CTR-2026-0041", contract_type="purchase",
            party_a_id="factory-id", party_b_id="factory-2", material_id="material-id",
            start_date=now - timedelta(days=10), end_date=now + timedelta(days=355),
            value=25000.0, terms="Net 30 payment terms. Buyer accepts liquid waste at minimum 80pct acid purity.",
            status="active"))
        db.commit()

    # ---- Payments ----
    if db.query(Payment).count() == 0:
        now = datetime.now(timezone.utc)
        db.add(Payment(id="pay-1", contract_id="con-1", amount=5000.0,
            payment_method="bank_transfer", status="completed",
            payment_date=now - timedelta(days=5), due_date=now + timedelta(days=25),
            paid_by="factory-id", paid_to="factory-2",
            reference_number="TXN-BANK-902487", invoice_number="INV-2026-01"))
        db.commit()

    # ---- Business Intelligence ----
    if db.query(BusinessIntelligence).count() == 0:
        now = datetime.now(timezone.utc)
        db.add(BusinessIntelligence(id="bi-1", report_type="sustainability",
            report_name="Q2 Environmental Impact Assessment", period="quarterly",
            start_date=now - timedelta(days=90), end_date=now,
            metrics={"total_co2_savings_tons": 4.69, "landfill_diversion_tons": 17.0, "water_recovery_liters": 450000},
            insights={"key_insight": "Waste substitution avoided 88pct of standard incineration footprint."},
            trends={"co2_savings_trend": [1.2, 1.5, 1.9]},
            generated_by="ai", confidence_score=0.95))
        db.commit()

    # ---- Anomaly Detections ----
    if db.query(AnomalyDetection).count() == 0:
        db.add(AnomalyDetection(id="ad-1", entity_type="price", entity_id="factory-id",
            anomaly_type="spike", severity="medium", anomaly_score=68.5,
            expected_value=85.0, actual_value=124.0, deviation_percentage=45.8,
            detection_method="Isolation Forest Outlier Model", status="resolved",
            resolution="Dynamic pricing updated baseline model due to high raw chemicals price index."))
        db.commit()

    # ---- Predictive Maintenance ----
    if db.query(PredictiveMaintenance).count() == 0:
        db.add(PredictiveMaintenance(id="pm-1", factory_id="factory-id",
            equipment_id="eq-centrifuge-04", equipment_name="Acid Recirculation Centrifuge",
            equipment_type="Centrifuge", health_score=82.4,
            predicted_failure_date=datetime.now(timezone.utc) + timedelta(days=74),
            confidence=89.0, risk_level="low",
            recommended_actions=["Schedule bearing lubrication within 30 days", "Calibrate flow velocity sensors"]))
        db.commit()

    logger.info("Database seeding complete!")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_columns()
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        logger.exception("Error seeding database: %s", str(e))
        db.rollback()
    finally:
        db.close()

