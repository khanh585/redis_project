from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel, redis
from starlette.requests import Request
import requests
import time

KEY = 'order_completed'

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

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending, completed, refunded

    class Meta:
        database = redis

@app.get("/order")
async def all():
    return [format(pk) for pk in Order.all_pks()]

def format(pk):
    order = Order.get(pk)
    return {
        "id": order.pk,
        "product_id": order.product_id,
        "price": order.price,
        "fee": order.fee,
        "total": order.total,
        "quantity": order.quantity,
        "status": order.status
    }


@app.post("/order")
async def create(request: Request, backgroup_tasks: BackgroundTasks):
    start = time.time()
    
    body = await request.json()
    req = requests.get(f'http://localhost:5000/products/%s' % body['product_id'])
    end = time.time()
    product = req.json()
    order = Order(
                    product_id = body['product_id'],
                    price = product['price'],
                    fee = product['price'] * 0.2 * body['quantity'],
                    total = product['price'] * 1.2 * body['quantity'],
                    quantity = body['quantity'],
                    status = "pending"
                )
    order.save()
    backgroup_tasks.add_task(order_completed, order)
    return order

def order_completed(order: Order):
    time.sleep(2)
    order.status = "completed"
    order.save()
    redis.xadd(KEY, order.dict(), '*')
    return 

@app.delete("/order/{pk}")
async def delete(pk:str):
    return Order.delete(pk=pk)

@app.get("/order/{pk}")
async def get(pk:str):
    return Order.get(pk=pk)
