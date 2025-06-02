from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.utils import db

router = APIRouter(prefix="/api/user", tags=["items"])


class ItemIn(BaseModel):
    name: str
    quantity: int = 1
    expiry_date: Optional[str] = None


class ItemOut(BaseModel):
    id: int
    name: str
    quantity: int
    date_added: str
    expiry_date: Optional[str]


@router.on_event("startup")
async def startup_event():
    await db.init_db()


@router.get("/{username}/items", response_model=List[ItemOut])
async def get_user_items(username: str):
    user_id = await db.get_user_id(username)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    items = await db.get_items(user_id)
    return items


@router.post("/{username}/items", response_model=ItemOut)
async def add_user_item(username: str, item: ItemIn):
    user_id = await db.add_user(username)
    await db.add_or_update_item(
        user_id, item.name, item.quantity, item.expiry_date
    )
    items = await db.get_items(user_id)
    # Return the item with the matching name (case-insensitive)
    for i in items:
        if i["name"].lower() == item.name.lower():
            return i
    return items[-1]  # fallback


@router.delete("/{username}/items/{item_id}")
async def delete_user_item(username: str, item_id: int):
    user_id = await db.get_user_id(username)
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not found")
    await db.remove_item(user_id, item_id)
    return {"status": "success", "message": "Item removed"} 