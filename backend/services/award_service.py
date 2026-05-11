"""
奖项服务模块

奖项管理的业务逻辑层，位于 Router 和 CRUD 之间。
职责：
- 协调 CRUD 操作调用
- ORM 模型 → Pydantic Schema 转换
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from schemas.award import Award, AwardCreate, AwardUpdate
from crud import award as award_crud


class AwardService:
    """奖项业务服务（无状态，方法接收 db session 作为参数）"""

    def get_all_awards(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        level: Optional[str] = None,
    ) -> tuple[List[Award], int]:
        """获取奖项列表（分页 + 搜索 + 过滤）"""
        models = award_crud.get_all(
            db, offset=offset, limit=limit, search=search, level=level
        )
        total = award_crud.count_all(db, search=search, level=level)
        return [Award.model_validate(m) for m in models], total

    def get_award_by_id(self, award_id: int, db: Session) -> Optional[Award]:
        """根据 ID 获取奖项详情"""
        model = award_crud.get_by_id(db, award_id)
        if not model:
            return None
        return Award.model_validate(model)

    def create_award(self, award_create: AwardCreate, db: Session) -> Award:
        """创建新奖项"""
        model = award_crud.create(db, award_create)
        return Award.model_validate(model)

    def update_award(
        self, award_id: int, award_update: AwardUpdate, db: Session
    ) -> Optional[Award]:
        """更新奖项（部分更新）"""
        model = award_crud.update(db, award_id, award_update)
        if not model:
            return None
        return Award.model_validate(model)

    def delete_award(self, award_id: int, db: Session) -> bool:
        """删除奖项"""
        return award_crud.delete(db, award_id)