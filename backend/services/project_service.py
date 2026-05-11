from typing import Optional, List
from sqlalchemy.orm import Session
from schemas.project import Project, ProjectCreate, ProjectUpdate
from crud import project_crud


class ProjectService:

    def get_all_projects(self, db: Session) -> List[Project]:
        models = project_crud.get_all(db)
        return [Project.model_validate(m) for m in models]

    def get_project_by_id(self, project_id: int, db: Session) -> Optional[Project]:
        model = project_crud.get_by_id(db, project_id)
        if not model:
            return None
        return Project.model_validate(model)

    def create_project(self, project_create: ProjectCreate, db: Session) -> Project:
        model = project_crud.create(db, project_create)
        return Project.model_validate(model)

    def update_project(self, project_id: int, project_update: ProjectUpdate, db: Session) -> Optional[Project]:
        model = project_crud.update(db, project_id, project_update)
        if not model:
            return None
        return Project.model_validate(model)

    def delete_project(self, project_id: int, db: Session) -> bool:
        return project_crud.delete(db, project_id)
