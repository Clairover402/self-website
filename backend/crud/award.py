"""
奖项 CRUD 操作模块

提供奖项的数据库增删改查操作。
使用 SQLAlchemy 2.0 风格的 select() 语句。
所有方法接收 Session 实例作为依赖注入。
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from models.award import AwardModel
from schemas.award import AwardCreate, AwardUpdate


def get_all(
    db: Session,
    offset: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    level: Optional[str] = None,
) -> list[AwardModel]:
    """
    获取奖项列表（支持分页、搜索、级别过滤）

    按 award_date 降序排列。
    """
    stmt = select(AwardModel)

    if search:
        like_pattern = f"%{search}%"
        stmt = stmt.where(
            AwardModel.title.like(like_pattern)
            | AwardModel.organization.like(like_pattern)
        )

    if level:
        stmt = stmt.where(AwardModel.level == level)

    stmt = stmt.order_by(AwardModel.award_date.desc()).offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()


def count_all(
    db: Session,
    search: Optional[str] = None,
    level: Optional[str] = None,
) -> int:
    """统计符合条件的奖项总数"""
    stmt = select(func.count(AwardModel.id))

    if search:
        like_pattern = f"%{search}%"
        stmt = stmt.where(
            AwardModel.title.like(like_pattern)
            | AwardModel.organization.like(like_pattern)
        )

    if level:
        stmt = stmt.where(AwardModel.level == level)

    return db.execute(stmt).scalar() or 0


def get_by_id(db: Session, award_id: int) -> Optional[AwardModel]:
    """根据 ID 查找单个奖项"""
    stmt = select(AwardModel).where(AwardModel.id == award_id)
    return db.execute(stmt).scalars().first()


def create(db: Session, award_create: AwardCreate) -> AwardModel:
    """创建新奖项"""
    award = AwardModel(
        title=award_create.title,
        organization=award_create.organization,
        award_date=award_create.award_date,
        level=award_create.level.value,
    )
    db.add(award)
    db.commit()
    db.refresh(award)
    return award


def update(db: Session, award_id: int, award_update: AwardUpdate) -> Optional[AwardModel]:
    """更新现有奖项（部分更新）"""
    award = get_by_id(db, award_id)
    if not award:
        return None

    update_data = award_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "level" and value is not None:
            value = value.value if hasattr(value, "value") else value
        setattr(award, key, value)

    award.updated_at = datetime.now()
    db.commit()
    db.refresh(award)
    return award


def delete(db: Session, award_id: int) -> bool:
    """删除奖项"""
    award = get_by_id(db, award_id)
    if not award:
        return False
    db.delete(award)
    db.commit()
    return True