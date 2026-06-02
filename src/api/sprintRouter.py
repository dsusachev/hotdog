import uuid
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.dependencies import getCurrentUser
from src.core.logger import logger
from src.db.database import getDb
from src.db.models.sprint import Sprint, SprintItem
from src.db.models.user import User

router = APIRouter(tags=["sprints"])


# ─── Schemas ────────────────────────────────────────────────────────────────


class SprintCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    start_date: date
    end_date: date
    total_points: int = Field(..., ge=1)


class SprintResponse(BaseModel):
    id: str
    name: str
    start_date: str
    end_date: str
    total_points: int
    created_at: str


class SprintItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    points: int = Field(1, ge=1)


class SprintItemResponse(BaseModel):
    id: str
    sprint_id: str
    title: str
    points: int
    is_done: bool
    done_at: str | None
    created_at: str


class BurndownPoint(BaseModel):
    date: str
    remaining_points: int
    ideal_remaining: float


class BurndownResponse(BaseModel):
    sprint_id: str
    sprint_name: str
    total_points: int
    start_date: str
    end_date: str
    data: list[BurndownPoint]


# ─── Helpers ─────────────────────────────────────────────────────────────────


def _requireAdmin(currentUser: User):
    if not settings.ADMIN_EMAIL or currentUser.email != settings.ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Доступ запрещён")


def _sprintResponse(s: Sprint) -> SprintResponse:
    return SprintResponse(
        id=str(s.id),
        name=s.name,
        start_date=s.start_date.isoformat(),
        end_date=s.end_date.isoformat(),
        total_points=s.total_points,
        created_at=s.created_at.isoformat(),
    )


def _itemResponse(i: SprintItem) -> SprintItemResponse:
    return SprintItemResponse(
        id=str(i.id),
        sprint_id=str(i.sprint_id),
        title=i.title,
        points=i.points,
        is_done=i.is_done,
        done_at=i.done_at.isoformat() if i.done_at else None,
        created_at=i.created_at.isoformat(),
    )


async def _getSprint(sprint_id: str, db: AsyncSession) -> Sprint:
    try:
        sid = uuid.UUID(sprint_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат id")
    result = await db.execute(select(Sprint).where(Sprint.id == sid))
    sprint = result.scalar_one_or_none()
    if not sprint:
        raise HTTPException(status_code=404, detail="Спринт не найден")
    return sprint


# ─── Sprint CRUD ─────────────────────────────────────────────────────────────


@router.get("/sprints", response_model=list[SprintResponse])
async def listSprints(db: AsyncSession = Depends(getDb)):
    result = await db.execute(select(Sprint).order_by(Sprint.start_date.desc()))
    return [_sprintResponse(s) for s in result.scalars().all()]


@router.get("/sprints/{sprintId}", response_model=SprintResponse)
async def getSprint(sprintId: str, db: AsyncSession = Depends(getDb)):
    return _sprintResponse(await _getSprint(sprintId, db))


@router.post("/sprints", response_model=SprintResponse, status_code=201)
async def createSprint(
    data: SprintCreate,
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    _requireAdmin(currentUser)
    if data.end_date <= data.start_date:
        raise HTTPException(
            status_code=400, detail="end_date должен быть позже start_date"
        )

    sprint = Sprint(
        id=uuid.uuid4(),
        name=data.name,
        start_date=data.start_date,
        end_date=data.end_date,
        total_points=data.total_points,
    )
    db.add(sprint)
    await db.commit()
    await db.refresh(sprint)
    logger.info(f"Sprint created: {sprint.name} by {currentUser.email}")
    return _sprintResponse(sprint)


@router.delete("/sprints/{sprintId}", status_code=204)
async def deleteSprint(
    sprintId: str,
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    _requireAdmin(currentUser)
    sprint = await _getSprint(sprintId, db)
    await db.delete(sprint)
    await db.commit()
    logger.info(f"Sprint deleted: {sprintId} by {currentUser.email}")


# ─── Sprint Items CRUD ───────────────────────────────────────────────────────


@router.get("/sprints/{sprintId}/items", response_model=list[SprintItemResponse])
async def listItems(sprintId: str, db: AsyncSession = Depends(getDb)):
    await _getSprint(sprintId, db)
    result = await db.execute(
        select(SprintItem)
        .where(SprintItem.sprint_id == uuid.UUID(sprintId))
        .order_by(SprintItem.created_at)
    )
    return [_itemResponse(i) for i in result.scalars().all()]


@router.post(
    "/sprints/{sprintId}/items", response_model=SprintItemResponse, status_code=201
)
async def addItem(
    sprintId: str,
    data: SprintItemCreate,
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    _requireAdmin(currentUser)
    await _getSprint(sprintId, db)

    item = SprintItem(
        id=uuid.uuid4(),
        sprint_id=uuid.UUID(sprintId),
        title=data.title,
        points=data.points,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return _itemResponse(item)


@router.patch(
    "/sprints/{sprintId}/items/{itemId}/done", response_model=SprintItemResponse
)
async def markItemDone(
    sprintId: str,
    itemId: str,
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    _requireAdmin(currentUser)
    try:
        iid = uuid.UUID(itemId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат id")

    result = await db.execute(
        select(SprintItem).where(
            SprintItem.id == iid,
            SprintItem.sprint_id == uuid.UUID(sprintId),
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    item.is_done = True
    item.done_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(item)
    logger.info(f"Item {itemId} marked done by {currentUser.email}")
    return _itemResponse(item)


# ─── Burndown Chart ──────────────────────────────────────────────────────────


@router.get(
    "/sprints/{sprintId}/burndown",
    response_model=BurndownResponse,
    summary="Burndown Chart спринта",
    description="Возвращает данные для построения Burndown Chart: фактические оставшиеся очки (`remaining_points`) и идеальная линия (`ideal_remaining`) для каждого дня от начала спринта до сегодня.",
)
async def getBurndown(sprintId: str, db: AsyncSession = Depends(getDb)):
    sprint = await _getSprint(sprintId, db)

    result = await db.execute(
        select(SprintItem).where(SprintItem.sprint_id == sprint.id)
    )
    items = result.scalars().all()

    total = sprint.total_points
    start = sprint.start_date
    end = sprint.end_date
    today = date.today()
    chart_end = min(end, today)

    num_days = (end - start).days or 1
    data = []
    current = start

    while current <= chart_end:
        # Очки выполненных задач на текущий день включительно
        burned = sum(
            i.points
            for i in items
            if i.is_done and i.done_at and i.done_at.date() <= current
        )
        remaining = max(total - burned, 0)

        # Идеальная линия: равномерное сгорание от total до 0
        elapsed = (current - start).days
        ideal = round(total * (1 - elapsed / num_days), 2)

        data.append(
            BurndownPoint(
                date=current.isoformat(),
                remaining_points=remaining,
                ideal_remaining=max(ideal, 0),
            )
        )
        current += timedelta(days=1)

    return BurndownResponse(
        sprint_id=str(sprint.id),
        sprint_name=sprint.name,
        total_points=total,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        data=data,
    )
