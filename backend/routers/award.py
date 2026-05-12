"""
奖项路由

定义奖项管理操作的 REST API 端点。
处理奖项的 CRUD 操作。
"""

import math
from typing import Optional
from schemas.common import PaginationParams, PaginatedResult
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.session import get_db
from schemas.award import Award, AwardCreate, AwardUpdate
from schemas.enums import AwardLevel
from services.award_service import AwardService
from utils.result import Result
from utils.exceptions import NotFoundException

router = APIRouter()
award_service = AwardService()


@router.get("/", response_model=Result[PaginatedResult[Award]])
async def get_awards(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="搜索关键词"),
    level: Optional[AwardLevel] = Query(default=None, description="按级别过滤"),
    db: Session = Depends(get_db),
):
    """获取奖项列表（分页）"""
    awards, total = award_service.get_all_awards(
        db,
        offset=pagination.offset,
        limit=pagination.limit,
        search=search,
        level=level.value if level else None,
    )

    total_pages = math.ceil(total / pagination.page_size) if total > 0 else 0

    return Result.ok(data=PaginatedResult[Award](
        items=awards,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
    ))


@router.get("/{award_id}", response_model=Result[Award])
async def get_award(award_id: int, db: Session = Depends(get_db)):
    """根据 ID 获取奖项详情"""
    award = award_service.get_award_by_id(award_id, db)
    if not award:
        raise NotFoundException(message="奖项未找到", err_code="AWARD_NOT_FOUND")
    return Result.ok(data=award)


@router.post("/", response_model=Result[Award])
async def create_award(award: AwardCreate, db: Session = Depends(get_db)):
    """创建新奖项"""
    new_award = award_service.create_award(award, db)
    return Result.ok(data=new_award)


@router.put("/{award_id}", response_model=Result[Award])
async def update_award(
    award_id: int,
    award_update: AwardUpdate,
    db: Session = Depends(get_db),
):
    """更新奖项（部分更新）"""
    updated_award = award_service.update_award(award_id, award_update, db)
    if not updated_award:
        raise NotFoundException(message="奖项未找到", err_code="AWARD_NOT_FOUND")
    return Result.ok(data=updated_award)


@router.delete("/{award_id}", response_model=Result[dict])
async def delete_award(award_id: int, db: Session = Depends(get_db)):
    """删除奖项"""
    success = award_service.delete_award(award_id, db)
    if not success:
        raise NotFoundException(message="奖项未找到", err_code="AWARD_NOT_FOUND")
    return Result.ok(data={"message": "奖项删除成功"})