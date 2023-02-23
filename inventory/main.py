from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5000'],
    allow_methods =['*'],
    allow_headers=['*'],
)

redis = get_redis_connection(
    host='redis-14308.c1.asia-northeast1-1.gce.cloud.redislabs.com', 
    port='14308',
    password='NoEzXy7tXO4buXW3FTwnmFkxoY2WOCAg',
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get("/products/{pk}")
async def get(pk:str):
    return Product.get(pk=pk)


@app.delete("/products/{pk}")
async def delete(pk:str):
    return Product.delete(pk=pk)


@app.get("/products")
async def all():
    return [format_product(pk) for pk in Product.all_pks()]


@app.post("/products")
async def create(product: Product):
    return product.save()


@app.put("/products/{pk}")
async def update(
    pk:str,
    product: Product):
    product.pk = pk
    return product.save()

def format_product(pk: str):
    product = Product.get(pk)
    return {
        "id": product.pk,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }
