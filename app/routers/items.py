import logging
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/items", tags=["items"])
logger = logging.getLogger(__name__)

fake_db = {1: {"name": "Foo", "price": 50.2, "is_offer": False}}


class Item(BaseModel):
    name: str = Field(..., title="Название", example="Телефон")
    price: float = Field(..., gt=0, title="Цена", example=199.99)
    is_offer: bool | None = Field(None, title="Акционный товар")


def _ensure_unique_name(name: str, exclude_id: int | None = None) -> None:
    target = name.strip().lower()
    for existing_id, existing_item in fake_db.items():
        if exclude_id is not None and existing_id == exclude_id:
            continue
        if existing_item["name"].strip().lower() == target:
            logger.warning("Попытка использовать неуникальное имя товара: %r", name)
            raise HTTPException(
                status_code=400,
                detail="Item with this name already exists",
            )


@router.get("/{item_id}", summary="Получить товар по ID")
def read_item(
    item_id: int = Path(..., title="ID товара", ge=1),
    q: str | None = Query(None, title="Поисковый запрос", max_length=50),
):
    if item_id not in fake_db:
        logger.warning("Товар с item_id=%s не найден", item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    logger.info("Получен товар item_id=%s (q=%r)", item_id, q)
    return {"item_id": item_id, "item": fake_db[item_id], "q": q}


@router.post("/", response_model=Item, status_code=201, summary="Создать товар")
def create_item(item: Item):
    _ensure_unique_name(item.name)
    new_id = max(fake_db.keys(), default=0) + 1
    fake_db[new_id] = item.model_dump()
    logger.info("Создан товар с id=%s и названием %r", new_id, item.name)
    return item


@router.put("/{item_id}", response_model=Item, summary="Обновить товар")
def update_item(
    item: Item,
    item_id: int = Path(..., title="ID товара", ge=1),
):
    if item_id not in fake_db:
        logger.warning("Попытка обновить несуществующий товар item_id=%s", item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    _ensure_unique_name(item.name, exclude_id=item_id)
    fake_db[item_id] = item.model_dump()
    logger.info("Обновлён товар item_id=%s", item_id)
    return item