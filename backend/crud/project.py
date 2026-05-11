from typing import Optional
from sqlalchemy.orm import Session
from models.project import ProjectModel
from schemas.project import ProjectCreate, ProjectUpdate


def get_all(db: Session) -> list[ProjectModel]:
    return db.query(ProjectModel).all()


def get_by_id(db: Session, project_id: int) -> Optional[ProjectModel]:
    return db.query(ProjectModel).filter(ProjectModel.id == project_id).first()


def create(db: Session, project_create: ProjectCreate) -> ProjectModel:
    project = ProjectModel(
        name=project_create.name,
        description=project_create.description,
        icon=project_create.icon,
        status=project_create.status,
        year=project_create.year,
        full_description=project_create.full_description,
        features=project_create.features or [],
        techs=project_create.techs or [],
        demo_url=project_create.demo_url,
        repo_url=project_create.repo_url,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update(db: Session, project_id: int, project_update: ProjectUpdate) -> Optional[ProjectModel]:
    project = get_by_id(db, project_id)
    if not project:
        return None
    update_data = project_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def delete(db: Session, project_id: int) -> bool:
    project = get_by_id(db, project_id)
    if not project:
        return False
    db.delete(project)
    db.commit()
    return True
