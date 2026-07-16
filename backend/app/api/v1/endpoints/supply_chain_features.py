from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
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


@router.post("/route-optimization", response_model=RouteOptimizationResponse)
def create_route_optimization(
    optimization: RouteOptimizationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create route optimization"""
    db_optimization = RouteOptimization(**optimization.dict())
    db.add(db_optimization)
    db.commit()
    db.refresh(db_optimization)
    return db_optimization


@router.get("/route-optimization/{shipment_id}", response_model=RouteOptimizationResponse)
def get_route_optimization(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get route optimization for a shipment"""
    optimization = db.query(RouteOptimization).filter(
        RouteOptimization.shipment_id == shipment_id
    ).first()
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
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@router.get("/inventory/{factory_id}", response_model=List[InventoryResponse])
def get_inventory(
    factory_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get inventory for a factory"""
    inventory = db.query(Inventory).filter(
        Inventory.factory_id == factory_id
    ).all()
    return inventory


@router.put("/inventory/{inventory_id}")
def update_inventory(
    inventory_id: str,
    current_stock: float,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update inventory stock"""
    inventory = db.query(Inventory).filter(
        Inventory.id == inventory_id
    ).first()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    inventory.current_stock = current_stock
    db.commit()
    return {"message": "Inventory updated successfully"}


@router.post("/supply-chain-visibility", response_model=SupplyChainVisibilityResponse)
def create_supply_chain_visibility(
    visibility: SupplyChainVisibilityCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create supply chain visibility record"""
    db_visibility = SupplyChainVisibility(**visibility.dict())
    db.add(db_visibility)
    db.commit()
    db.refresh(db_visibility)
    return db_visibility


@router.get("/supply-chain-visibility/{material_id}", response_model=List[SupplyChainVisibilityResponse])
def get_supply_chain_visibility(
    material_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get supply chain visibility for a material"""
    visibility = db.query(SupplyChainVisibility).filter(
        SupplyChainVisibility.material_id == material_id
    ).all()
    return visibility


@router.get("/shipment-tracking/{shipment_id}")
def get_shipment_tracking(
    shipment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get shipment tracking information"""
    tracking = db.query(ShipmentTracking).filter(
        ShipmentTracking.shipment_id == shipment_id
    ).first()
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
    performance = db.query(SupplierPerformance).filter(
        SupplierPerformance.supplier_id == supplier_id
    ).order_by(SupplierPerformance.updated_at.desc()).first()
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
    costs = db.query(LogisticsCost).filter(
        LogisticsCost.shipment_id == shipment_id
    ).all()
    return costs
