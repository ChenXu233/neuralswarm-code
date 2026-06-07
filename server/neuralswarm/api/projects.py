import os
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from neuralswarm.database import get_db
from neuralswarm.models.project import Project
from neuralswarm.schemas.project import ProjectCreate, ProjectListResponse, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("")
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)):
    if not os.path.exists(body.path):
        raise HTTPException(status_code=400, detail=f"Path does not exist: {body.path}")
    if not os.path.isdir(body.path):
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {body.path}")

    normalized = body.path.replace("\\", "/")
    path_uri = f"server:///{normalized.lstrip('/')}"

    project = Project(name=body.name, path=path_uri)
    db.add(project)
    await db.commit()
    await db.refresh(project)

    return {"data": ProjectResponse.model_validate(project).model_dump()}


@router.get("")
async def list_projects(limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    count_stmt = select(func.count()).select_from(Project).where(Project.deleted_at.is_(None))
    total = (await db.execute(count_stmt)).scalar_one()

    stmt = select(Project).where(Project.deleted_at.is_(None)).offset(offset).limit(limit).order_by(Project.created_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()

    return {"items": [ProjectResponse.model_validate(p).model_dump() for p in projects], "total": total}


@router.get("/{project_id}")
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    try:
        pid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Project not found")
    stmt = select(Project).where(Project.id == pid, Project.deleted_at.is_(None))
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"data": ProjectResponse.model_validate(project).model_dump()}


@router.delete("/{project_id}")
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    try:
        pid = UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Project not found")
    stmt = select(Project).where(Project.id == pid, Project.deleted_at.is_(None))
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.deleted_at = datetime.now(timezone.utc)
    await db.commit()
    return {"data": {"id": str(project.id), "deleted": True}}
