import aiosqlite
import os
from typing import List, Dict, Any, Optional

DB_PATH = os.getenv("FRIDGE_DB_PATH", "fridge.db")


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                date_added TEXT DEFAULT CURRENT_TIMESTAMP,
                expiry_date TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        await db.commit()


async def add_user(username: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'INSERT OR IGNORE INTO users (username) VALUES (?)', (username,)
        )
        await db.commit()
        cursor = await db.execute(
            'SELECT id FROM users WHERE username = ?', (username,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def get_user_id(username: str) -> Optional[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id FROM users WHERE username = ?', (username,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None


async def add_item(
    user_id: int,
    name: str,
    quantity: int = 1,
    expiry_date: Optional[str] = None
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO items (user_id, name, quantity, expiry_date) '
            'VALUES (?, ?, ?, ?)',
            (user_id, name, quantity, expiry_date)
        )
        await db.commit()


async def add_or_update_item(
    user_id: int,
    name: str,
    quantity: int = 1,
    expiry_date: Optional[str] = None
):
    async with aiosqlite.connect(DB_PATH) as db:
        # Check if item exists (case-insensitive)
        cursor = await db.execute(
            'SELECT id, quantity FROM items WHERE user_id = ? '
            'AND LOWER(name) = LOWER(?)',
            (user_id, name)
        )
        row = await cursor.fetchone()
        if row:
            item_id, old_quantity = row
            new_quantity = old_quantity + quantity
            if expiry_date:
                await db.execute(
                    'UPDATE items SET quantity = ?, expiry_date = ? '
                    'WHERE id = ?',
                    (new_quantity, expiry_date, item_id)
                )
            else:
                await db.execute(
                    'UPDATE items SET quantity = ? WHERE id = ?',
                    (new_quantity, item_id)
                )
        else:
            await db.execute(
                'INSERT INTO items (user_id, name, quantity, expiry_date) '
                'VALUES (?, ?, ?, ?)',
                (user_id, name, quantity, expiry_date)
            )
        await db.commit()


async def get_items(user_id: int) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'SELECT id, name, quantity, date_added, expiry_date '
            'FROM items WHERE user_id = ?',
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "quantity": row[2],
                "date_added": row[3],
                "expiry_date": row[4],
            }
            for row in rows
        ]


async def remove_item(user_id: int, item_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'DELETE FROM items WHERE user_id = ? AND id = ?',
            (user_id, item_id)
        )
        await db.commit() 