import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.dependencies import getCurrentUser
from src.core.logger import logger
from src.db.database import getDb
from src.db.models.category import Category
from src.db.models.user import User

router = APIRouter(tags=["categories"])


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9_-]+$")


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    slug: str | None = Field(
        None, min_length=1, max_length=100, pattern=r"^[a-z0-9_-]+$"
    )


class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str


class CategoryVersionResponse(BaseModel):
    version: str
    count: int


class CategoryListResponse(BaseModel):
    version: str
    count: int
    categories: list[CategoryResponse]


def _requireAdmin(currentUser: User):
    if not settings.ADMIN_EMAIL or currentUser.email != settings.ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Доступ запрещён")


def _computeVersion(categories: list[Category]) -> str:
    """SHA-256 хеш от отсортированных name+slug — меняется при любом изменении."""
    payload = "|".join(
        f"{c.name}:{c.slug}" for c in sorted(categories, key=lambda c: c.slug)
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


async def _fetchAll(db: AsyncSession) -> list[Category]:
    result = await db.execute(select(Category).order_by(Category.name))
    return result.scalars().all()


@router.get(
    "/categories/version",
    response_model=CategoryVersionResponse,
    summary="Версия справочника категорий",
    description="Возвращает короткий хеш (SHA-256) текущего состояния справочника. Используйте для кеширования: если версия не изменилась — полный список можно не запрашивать.",
)
async def getCategoriesVersion(db: AsyncSession = Depends(getDb)):
    categories = await _fetchAll(db)
    return CategoryVersionResponse(
        version=_computeVersion(categories),
        count=len(categories),
    )


@router.get(
    "/categories",
    response_model=CategoryListResponse,
    summary="Список категорий с версией",
    description="Возвращает все категории вместе с версией справочника для клиентского кеширования.",
)
async def listCategories(db: AsyncSession = Depends(getDb)):
    categories = await _fetchAll(db)
    version = _computeVersion(categories)
    logger.info(f"Categories list: {len(categories)} items, version={version}")
    return CategoryListResponse(
        version=version,
        count=len(categories),
        categories=[
            CategoryResponse(id=str(c.id), name=c.name, slug=c.slug) for c in categories
        ],
    )


@router.get("/categories/{categoryId}", response_model=CategoryResponse)
async def getCategory(categoryId: str, db: AsyncSession = Depends(getDb)):
    try:
        cat_uuid = uuid.UUID(categoryId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат id")

    result = await db.execute(select(Category).where(Category.id == cat_uuid))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    return CategoryResponse(id=str(category.id), name=category.name, slug=category.slug)


@router.post("/categories", response_model=CategoryListResponse, status_code=201)
async def createCategory(
    data: CategoryCreate,
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    _requireAdmin(currentUser)

    existing = await db.execute(
        select(Category).where(
            (Category.name == data.name) | (Category.slug == data.slug)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="Категория с таким именем или slug уже существует"
        )

    category = Category(id=uuid.uuid4(), name=data.name, slug=data.slug)
    db.add(category)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail="Категория с таким именем или slug уже существует"
        )

    categories = await _fetchAll(db)
    version = _computeVersion(categories)
    logger.info(
        f"Category created: {category.name} by {currentUser.email}, new version={version}"
    )
    return CategoryListResponse(
        version=version,
        count=len(categories),
        categories=[
            CategoryResponse(id=str(c.id), name=c.name, slug=c.slug) for c in categories
        ],
    )


@router.patch("/categories/{categoryId}", response_model=CategoryListResponse)
async def updateCategory(
    categoryId: str,
    data: CategoryUpdate,
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    _requireAdmin(currentUser)

    try:
        cat_uuid = uuid.UUID(categoryId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат id")

    result = await db.execute(select(Category).where(Category.id == cat_uuid))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    if data.name is not None:
        category.name = data.name
    if data.slug is not None:
        category.slug = data.slug

    await db.commit()

    categories = await _fetchAll(db)
    version = _computeVersion(categories)
    logger.info(
        f"Category updated: {category.name} by {currentUser.email}, new version={version}"
    )
    return CategoryListResponse(
        version=version,
        count=len(categories),
        categories=[
            CategoryResponse(id=str(c.id), name=c.name, slug=c.slug) for c in categories
        ],
    )


@router.delete("/categories/{categoryId}", response_model=CategoryVersionResponse)
async def deleteCategory(
    categoryId: str,
    db: AsyncSession = Depends(getDb),
    currentUser: User = Depends(getCurrentUser),
):
    _requireAdmin(currentUser)

    try:
        cat_uuid = uuid.UUID(categoryId)
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат id")

    result = await db.execute(select(Category).where(Category.id == cat_uuid))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Категория не найдена")

    await db.delete(category)
    await db.commit()

    categories = await _fetchAll(db)
    version = _computeVersion(categories)
    logger.info(
        f"Category deleted: {categoryId} by {currentUser.email}, new version={version}"
    )
    return CategoryVersionResponse(version=version, count=len(categories))
