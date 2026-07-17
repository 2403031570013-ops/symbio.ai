import asyncio
from dataclasses import dataclass
from typing import Any, Iterable

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings
from app.models.ai_recommendations import AIRecommendation, DemandPrediction, PriceForecast
from app.models.analytics import Analytics
from app.models.auth import EmailOtp, MobileOtp, RefreshToken
from app.models.compliance_risk import AuditTrail, ComplianceCheck, DocumentCompliance, FraudDetection, RegulatoryUpdate, RiskAssessment
from app.models.esg_sustainability import CarbonCredit, CarbonFootprint, ESGScore, GreenCertification, SustainabilityDashboard, WasteImpact
from app.models.factory import Factory
from app.models.marketplace_operations import AnomalyDetection, BusinessIntelligence, Contract, DynamicPricing, Payment, PredictiveMaintenance, SmartNotification, WorkflowAutomation
from app.models.material import Material
from app.models.match import Match
from app.models.messaging import Conversation, Message
from app.models.notification import Notification
from app.models.storage import StoredObject
from app.models.supply_chain import Inventory, LogisticsCost, RouteOptimization, ShipmentTracking, SupplierPerformance, SupplyChainVisibility
from app.models.transaction import Transaction
from app.models.user import User

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


def _run(coro):
    return asyncio.run(coro)


@dataclass
class _AggregateExpr:
    op: str
    field: Any | None = None
    default: Any | None = None


class _FuncNamespace:
    def sum(self, field: Any) -> _AggregateExpr:
        return _AggregateExpr("sum", field)

    def count(self, field: Any) -> _AggregateExpr:
        return _AggregateExpr("count", field)

    def coalesce(self, expr: Any, default: Any) -> _AggregateExpr:
        return _AggregateExpr("coalesce", expr, default)


func = _FuncNamespace()


def or_(*conditions: Any) -> Any:
    conditions = [condition for condition in conditions if condition is not None]
    if not conditions:
        return None
    combined = conditions[0]
    for condition in conditions[1:]:
        combined = combined | condition
    return combined


def desc(field: Any) -> Any:
    return -field if hasattr(field, "__neg__") else field.desc()


class _Dialect:
    name = "mongodb"


class _Bind:
    dialect = _Dialect()


class MongoQuery:
    def __init__(self, model_or_expr: Any, projection: Iterable[Any] | None = None):
        self.model_or_expr = model_or_expr
        self.projection = tuple(projection or ())
        self.conditions: list[Any] = []
        self.sort_fields: list[Any] = []
        self.limit_value: int | None = None
        self.offset_value: int = 0
        self.group_field: Any | None = None

    def filter(self, *conditions: Any):
        self.conditions.extend([condition for condition in conditions if condition is not None])
        return self

    def order_by(self, *fields: Any):
        self.sort_fields.extend(fields)
        return self

    def group_by(self, *fields: Any):
        self.group_field = fields[0] if fields else None
        return self

    def limit(self, value: int):
        self.limit_value = value
        return self

    def offset(self, value: int):
        self.offset_value = value
        return self

    def _build_condition(self):
        if not self.conditions:
            return None
        combined = self.conditions[0]
        for condition in self.conditions[1:]:
            combined = combined & condition
        return combined

    async def _fetch_many(self):
        condition = self._build_condition()
        model = self.model_or_expr if isinstance(self.model_or_expr, type) else None
        if model is None:
            return []
        query = model.find(condition) if condition is not None else model.find_all()
        for field in self.sort_fields:
            query = query.sort(field)
        if self.offset_value:
            query = query.skip(self.offset_value)
        if self.limit_value is not None:
            query = query.limit(self.limit_value)
        return await query.to_list()

    async def _fetch_one(self):
        items = await self._fetch_many()
        return items[0] if items else None

    async def _count(self):
        if isinstance(self.model_or_expr, type):
            condition = self._build_condition()
            query = self.model_or_expr.find(condition) if condition is not None else self.model_or_expr.find_all()
            return await query.count()
        items = await self._fetch_many()
        return len(items)

    async def _scalar(self):
        expr = self.model_or_expr
        if isinstance(expr, _AggregateExpr):
            if expr.op == "coalesce" and isinstance(expr.field, _AggregateExpr):
                nested = await MongoQuery(expr.field.field).filter(*self.conditions)._scalar()
                return nested if nested not in (None, 0, "") else expr.default
            if expr.op == "sum":
                docs = await self._fetch_many()
                field_name = getattr(expr.field, "field_name", None) or getattr(expr.field, "name", None)
                return sum(float(getattr(doc, field_name, 0) or 0) for doc in docs)
            if expr.op == "count":
                return await self._count()
        return None

    async def _grouped_rows(self):
        docs = await self._fetch_many()
        group_field = self.group_field
        value_field = self.projection[1] if len(self.projection) > 1 else None
        group_name = getattr(group_field, "field_name", None) or getattr(group_field, "name", None)
        value_name = getattr(value_field, "field_name", None) or getattr(value_field, "name", None)
        buckets: dict[Any, int] = {}
        for doc in docs:
            key = getattr(doc, group_name, None)
            buckets[key] = buckets.get(key, 0) + 1
        if value_name is None:
            return [(key, count) for key, count in buckets.items()]
        return [(key, count) for key, count in buckets.items()]

    def all(self):
        if self.group_field is not None:
            return _run(self._grouped_rows())
        return _run(self._fetch_many())

    def first(self):
        return _run(self._fetch_one())

    def scalar(self):
        return _run(self._scalar())

    def count(self):
        return _run(self._count())

    def delete(self, synchronize_session: bool | None = None):
        docs = self.all()
        for doc in docs:
            _run(doc.delete())
        return len(docs)

    def update(self, values: dict[str, Any], synchronize_session: bool | None = None):
        docs = self.all()
        for doc in docs:
            for key, value in values.items():
                setattr(doc, key, value)
            _run(doc.save())
        return len(docs)


class MongoSession:
    bind = _Bind()

    def query(self, *entities: Any):
        if len(entities) == 1:
            return MongoQuery(entities[0])
        return MongoQuery(entities[0], projection=entities)

    def add(self, instance: Any):
        _run(instance.insert())

    def add_all(self, instances: Iterable[Any]):
        for instance in instances:
            self.add(instance)

    def delete(self, instance: Any):
        _run(instance.delete())

    def commit(self):
        return None

    def rollback(self):
        return None

    def refresh(self, instance: Any):
        return instance

    def close(self):
        return None


SessionLocal = MongoSession


async def connect_to_mongo():
    """Connect to MongoDB using Motor and initialize Beanie."""
    global client, database
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    database = client[settings.DATABASE_NAME]

    await init_beanie(
        database=database,
        document_models=[
            User, Factory, Material, Transaction, Match, Analytics,
            AIRecommendation, DemandPrediction, PriceForecast,
            CarbonFootprint, ESGScore, SustainabilityDashboard, WasteImpact, GreenCertification, CarbonCredit,
            RouteOptimization, Inventory, SupplyChainVisibility, ShipmentTracking, SupplierPerformance, LogisticsCost,
            ComplianceCheck, RiskAssessment, AuditTrail, DocumentCompliance,
            RegulatoryUpdate,
            DynamicPricing, SmartNotification, WorkflowAutomation, Contract, Payment, BusinessIntelligence, AnomalyDetection, PredictiveMaintenance,
            RefreshToken, EmailOtp, MobileOtp,
            Conversation, Message, Notification, StoredObject,
            FraudDetection,
        ],
    )


async def close_mongo():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()


def get_database() -> AsyncIOMotorDatabase:
    """Get the async database instance."""
    if database is None:
        raise RuntimeError("MongoDB is not connected")
    return database


