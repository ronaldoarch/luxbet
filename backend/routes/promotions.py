"""
Rotas para gerenciamento de promoções
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, date, timezone

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
    print(f"[Promotions Update] ID={promotion_id}, updating fields: {list(update_data.keys())}")
    for field, value in update_data.items():
        print(f"  - {field}: {value} (type: {type(value).__name__})")
        setattr(promotion, field, value)
    
    db.commit()
    db.refresh(promotion)
    print(f"[Promotions Update] After update - active={promotion.is_active}, featured={promotion.is_featured}, start={promotion.start_date}, end={promotion.end_date}")
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
    # Usar UTC para comparação consistente
    today_utc = datetime.now(timezone.utc).date()
    query = db.query(Promotion).filter(
        Promotion.is_active == True,
        func.date(Promotion.start_date) <= today_utc,
        func.date(Promotion.end_date) >= today_utc
    )
    
    if featured is True:
        query = query.filter(Promotion.is_featured == True)
    
    promotions = query.order_by(desc(Promotion.position), desc(Promotion.created_at)).limit(limit).all()
    # Log para debug
    print(f"[Promotions API] featured={featured}, today_utc={today_utc}, found={len(promotions)} promotions")
    if promotions:
        for p in promotions:
            print(f"  - {p.id}: {p.title} (active={p.is_active}, featured={p.is_featured}, start={p.start_date.date()}, end={p.end_date.date()})")
    return promotions


@public_router.get("/debug")
async def debug_promotions(
    db: Session = Depends(get_db)
):
    """Endpoint de debug para verificar promoções (temporário)"""
    today_utc = datetime.now(timezone.utc).date()
    all_promos = db.query(Promotion).all()
    active_promos = db.query(Promotion).filter(Promotion.is_active == True).all()
    featured_promos = db.query(Promotion).filter(
        Promotion.is_active == True,
        Promotion.is_featured == True
    ).all()
    valid_promos = db.query(Promotion).filter(
        Promotion.is_active == True,
        func.date(Promotion.start_date) <= today_utc,
        func.date(Promotion.end_date) >= today_utc
    ).all()
    valid_featured = db.query(Promotion).filter(
        Promotion.is_active == True,
        Promotion.is_featured == True,
        func.date(Promotion.start_date) <= today_utc,
        func.date(Promotion.end_date) >= today_utc
    ).all()
    
    return {
        "today_utc": str(today_utc),
        "total": len(all_promos),
        "active": len(active_promos),
        "featured": len(featured_promos),
        "valid": len(valid_promos),
        "valid_featured": len(valid_featured),
        "promotions": [{
            "id": p.id,
            "title": p.title,
            "is_active": p.is_active,
            "is_featured": p.is_featured,
            "start_date": str(p.start_date),
            "end_date": str(p.end_date),
            "start_date_only": str(func.date(p.start_date)),
            "end_date_only": str(func.date(p.end_date)),
            "valid": func.date(p.start_date) <= today_utc and func.date(p.end_date) >= today_utc
        } for p in all_promos]
    }


@public_router.get("/{promotion_id}", response_model=PromotionResponse)
async def get_public_promotion(
    promotion_id: int,
    db: Session = Depends(get_db)
):
    """Obter promoção por ID (público)"""
    today_utc = datetime.now(timezone.utc).date()
    promotion = db.query(Promotion).filter(
        Promotion.id == promotion_id,
        Promotion.is_active == True,
        func.date(Promotion.start_date) <= today_utc,
        func.date(Promotion.end_date) >= today_utc
    ).first()
    
    if not promotion:
        raise HTTPException(status_code=404, detail="Promoção não encontrada ou expirada")
    
    return promotion
