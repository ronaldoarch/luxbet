"""
Rotas para gerenciamento de promoções
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, date

from database import get_db
from dependencies import get_current_admin_user, get_current_user
from models import User, Promotion, PromotionType
from schemas import (
    PromotionResponse, PromotionCreate, PromotionUpdate
)

router = APIRouter(prefix="/api/admin/promotions", tags=["promotions"])
public_router = APIRouter(prefix="/api/public/promotions", tags=["public-promotions"])


# ========== ADMIN ROUTES ==========

@router.get("", response_model=List[PromotionResponse])
async def list_promotions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Listar todas as promoções (admin)"""
    query = db.query(Promotion)
    
    if is_active is not None:
        query = query.filter(Promotion.is_active == is_active)
    
    promotions = query.order_by(desc(Promotion.position), desc(Promotion.created_at)).offset(skip).limit(limit).all()
    return promotions


@router.get("/{promotion_id}", response_model=PromotionResponse)
async def get_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Obter promoção por ID (admin)"""
    promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promoção não encontrada")
    return promotion


@router.post("", response_model=PromotionResponse, status_code=status.HTTP_201_CREATED)
async def create_promotion(
    promotion_data: PromotionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Criar nova promoção"""
    promotion = Promotion(**promotion_data.model_dump())
    db.add(promotion)
    db.commit()
    db.refresh(promotion)
    return promotion


@router.put("/{promotion_id}", response_model=PromotionResponse)
async def update_promotion(
    promotion_id: int,
    promotion_data: PromotionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Atualizar promoção"""
    promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promoção não encontrada")
    
    update_data = promotion_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(promotion, field, value)
    
    db.commit()
    db.refresh(promotion)
    return promotion


@router.delete("/{promotion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_promotion(
    promotion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Deletar promoção"""
    promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
    if not promotion:
        raise HTTPException(status_code=404, detail="Promoção não encontrada")
    
    db.delete(promotion)
    db.commit()
    return None


# ========== PUBLIC ROUTES ==========

@public_router.get("", response_model=List[PromotionResponse])
async def list_public_promotions(
    featured: Optional[bool] = Query(None, description="Apenas promoções em destaque"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Listar promoções ativas (público) - usa comparação por data para evitar problemas de timezone"""
    today = date.today()
    query = db.query(Promotion).filter(
        Promotion.is_active == True,
        func.date(Promotion.start_date) <= today,
        func.date(Promotion.end_date) >= today
    )
    
    if featured is True:
        query = query.filter(Promotion.is_featured == True)
    
    promotions = query.order_by(desc(Promotion.position), desc(Promotion.created_at)).limit(limit).all()
    return promotions


@public_router.get("/{promotion_id}", response_model=PromotionResponse)
async def get_public_promotion(
    promotion_id: int,
    db: Session = Depends(get_db)
):
    """Obter promoção por ID (público)"""
    today = date.today()
    promotion = db.query(Promotion).filter(
        Promotion.id == promotion_id,
        Promotion.is_active == True,
        func.date(Promotion.start_date) <= today,
        func.date(Promotion.end_date) >= today
    ).first()
    
    if not promotion:
        raise HTTPException(status_code=404, detail="Promoção não encontrada ou expirada")
    
    return promotion
