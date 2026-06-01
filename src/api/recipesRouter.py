from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List

from src.core.logger import logger
from src.services.mealDbClient import mealDbClient, CATEGORY_MAP

router = APIRouter()


class RecipeCard(BaseModel):
    id: str
    name: str
    category: str
    image_url: str


class Ingredient(BaseModel):
    name: str
    measure: str


class RecipeDetail(BaseModel):
    id: str
    name: str
    category: str
    area: str | None
    image_url: str
    instructions: str
    ingredients: List[Ingredient]
    youtube: str | None


def _normalize_thumb(url: str) -> str:
    if url and not any(url.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.webp')):
        return url + '/preview'
    return url


def _parse_ingredients(meal: dict) -> List[Ingredient]:
    result = []
    for i in range(1, 21):
        name = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if name:
            result.append(Ingredient(name=name, measure=measure))
    return result


@router.get("/recipes", response_model=List[RecipeCard])
async def getRecipes(
    category: str = Query("all", description="all | breakfast | lunch | dinner | snack"),
):
    logger.info(f"Fetching recipes, category={category}")

    if category == "all":
        # Берём по одной странице из каждой категории
        meals = []
        for cat in CATEGORY_MAP.values():
            page = await mealDbClient.getByCategory(cat)
            meals.extend(page[:5])
    else:
        en_cat = CATEGORY_MAP.get(category)
        if not en_cat:
            raise HTTPException(status_code=400, detail=f"Unknown category: {category}")
        meals = await mealDbClient.getByCategory(en_cat)

    cards = [
        RecipeCard(
            id=m["idMeal"],
            name=m["strMeal"],
            category=category,
            image_url=_normalize_thumb(m["strMealThumb"]),
        )
        for m in meals
        if m.get("idMeal") and m.get("strMeal")
    ]
    return cards


@router.get("/recipes/{recipe_id}", response_model=RecipeDetail)
async def getRecipe(recipe_id: str):
    logger.info(f"Fetching recipe detail: {recipe_id}")
    meal = await mealDbClient.getById(recipe_id)
    if not meal:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return RecipeDetail(
        id=meal["idMeal"],
        name=meal["strMeal"],
        category=meal.get("strCategory") or "",
        area=meal.get("strArea"),
        image_url=meal["strMealThumb"],
        instructions=meal.get("strInstructions") or "",
        ingredients=_parse_ingredients(meal),
        youtube=meal.get("strYoutube") or None,
    )
