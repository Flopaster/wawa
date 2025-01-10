from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import asyncpg
from contextlib import asynccontextmanager

DATABASE_URL = "postgresql://postgres:your_password@localhost:5432/your_database_name"

class Dish(BaseModel):
    id: int
    name: str
    description: str
    price: float

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(DATABASE_URL)
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/dishes/", response_model=List[Dish])
async def get_dishes():
    async with app.state.pool.acquire() as connection:
        dishes = await connection.fetch("SELECT * FROM dishes")
        return [Dish(id=dish["id"], name=dish["name"], description=dish["description"], price=dish["price"]) for dish in dishes]

@app.get("/dishes/{dish_id}", response_model=Dish)
async def get_dish(dish_id: int):
    async with app.state.pool.acquire() as connection:
        dish = await connection.fetchrow("SELECT * FROM dishes WHERE id = \$1", dish_id)
        if dish:
            return Dish(id=dish["id"], name=dish["name"], description=dish["description"], price=dish["price"])
        raise HTTPException(status_code=404, detail="Dish not found")

@app.post("/dishes/", response_model=Dish)
async def create_dish(dish: Dish):
    async with app.state.pool.acquire() as connection:
        new_dish_id = await connection.fetchval(
            "INSERT INTO dishes (id, name, description, price) VALUES (\$1, \$2, \$3, \$4) RETURNING id",
            dish.id, dish.name, dish.description, dish.price
        )
        return Dish(id=new_dish_id, **dish.dict())

@app.put("/dishes/{dish_id}", response_model=Dish)
async def update_dish(dish_id: int, updated_dish: Dish):
    async with app.state.pool.acquire() as connection:
        result = await connection.execute(
            "UPDATE dishes SET name = \$1, description = \$2, price = \$3 WHERE id = \$4",
            updated_dish.name, updated_dish.description, updated_dish.price, dish_id
        )
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Dish not found")
        return updated_dish

@app.delete("/dishes/{dish_id}")
async def delete_dish(dish_id: int):
    async with app.state.pool.acquire() as connection:
        result = await connection.execute("DELETE FROM dishes WHERE id = \$1", dish_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Dish not found")
        return {"message": "Dish deleted successfully"}