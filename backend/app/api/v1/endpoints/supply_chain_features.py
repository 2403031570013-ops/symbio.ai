import asyncio
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from app.models.supply_chain import (
    RouteOptimization, Inventory, SupplyChainVisibility,
    ShipmentTracking, SupplierPerformance, LogisticsCost
)
from app.schemas.supply_chain import (
    RouteOptimizationCreate, RouteOptimizationResponse,
    InventoryCreate, InventoryResponse,
    SupplyChainVisibilityCreate, SupplyChainVisibilityResponse
)
from app.core.security import get_current_user

router = APIRouter()

Session = Any


def get_db() -> None:
    return None


def _run(coro):
    return asyncio.run(coro)


@router.post("/route-optimization", response_model=RouteOptimizationResponse)
def create_route_optimization(
    optimization: RouteOptimizationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create route optimization"""
    db_optimization = RouteOptimization(**optimization.dict())
    _run(db_optimization.insert())
    return db_optimization


@router.get("/route-optimization/{shipment_id}", response_model=RouteOptimizationResponse)
def get_route_optimization(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get route optimization for a shipment"""
    optimization = _run(RouteOptimization.find_one(RouteOptimization.shipment_id == shipment_id))
    if not optimization:
        raise HTTPException(status_code=404, detail="Route optimization not found")
    return optimization


@router.post("/inventory", response_model=InventoryResponse)
def create_inventory(
    inventory: InventoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create inventory record"""
    db_inventory = Inventory(**inventory.dict())
    _run(db_inventory.insert())
    return db_inventory


@router.get("/inventory/{factory_id}", response_model=List[InventoryResponse])
def get_inventory(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get inventory for a factory"""
    inventory = _run(Inventory.find(Inventory.factory_id == factory_id).to_list())
    return inventory


@router.put("/inventory/{inventory_id}")
def update_inventory(
    inventory_id: str,
    current_stock: float,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update inventory stock"""
    inventory = _run(Inventory.find_one(Inventory.id == inventory_id))
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    inventory.current_stock = current_stock
    _run(inventory.save())
    return {"message": "Inventory updated successfully"}


@router.post("/supply-chain-visibility", response_model=SupplyChainVisibilityResponse)
def create_supply_chain_visibility(
    visibility: SupplyChainVisibilityCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create supply chain visibility record"""
    db_visibility = SupplyChainVisibility(**visibility.dict())
    _run(db_visibility.insert())
    return db_visibility


@router.get("/supply-chain-visibility/{material_id}", response_model=List[SupplyChainVisibilityResponse])
def get_supply_chain_visibility(
    material_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get supply chain visibility for a material"""
    visibility = _run(SupplyChainVisibility.find(SupplyChainVisibility.material_id == material_id).to_list())
    return visibility


@router.get("/shipment-tracking/{shipment_id}")
def get_shipment_tracking(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get shipment tracking information"""
    tracking = _run(ShipmentTracking.find_one(ShipmentTracking.shipment_id == shipment_id))
    if not tracking:
        raise HTTPException(status_code=404, detail="Shipment tracking not found")
    return tracking


@router.get("/supplier-performance/{supplier_id}")
def get_supplier_performance(
    supplier_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get supplier performance metrics"""
    performance = _run(SupplierPerformance.find(SupplierPerformance.supplier_id == supplier_id).sort(-SupplierPerformance.updated_at).first_or_none())
    if not performance:
        raise HTTPException(status_code=404, detail="Supplier performance not found")
    return performance


@router.get("/logistics-cost/{shipment_id}")
def get_logistics_cost(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get logistics cost breakdown"""
    costs = _run(LogisticsCost.find(LogisticsCost.shipment_id == shipment_id).to_list())
    return costs
