from fastapi import APIRouter
from app.api.v1.endpoints import (
    admin, analytics, auth, factories, materials, matches, 
    shipments, transactions, ai_features, esg_features, 
    supply_chain_features, compliance_features, marketplace_features, messaging, storage, notifications
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(factories.router, prefix="/factories", tags=["factories"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["shipments"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(ai_features.router, prefix="/ai", tags=["ai-features"])
api_router.include_router(esg_features.router, prefix="/esg", tags=["esg-sustainability"])
api_router.include_router(supply_chain_features.router, prefix="/supply-chain", tags=["supply-chain"])
api_router.include_router(compliance_features.router, prefix="/compliance", tags=["compliance-risk"])
api_router.include_router(marketplace_features.router, prefix="/marketplace", tags=["marketplace-operations"])
api_router.include_router(messaging.router, prefix="/messaging", tags=["messaging"])
api_router.include_router(storage.router, prefix="/storage", tags=["storage"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
