from main import redis,Order
import time

key_refunded = 'order_refunded'
group = 'payment-group'

try:
    redis.xgroup_create(key_refunded, group)
except:
    print('Group already exists')

while True:
    try:
        results = redis.xreadgroup(group, key_refunded, {key_refunded: '>'}, None)
        if results:
            for result in results:
                obj = result[1][0][1]
                order = Order.get(obj['pk'])
                print(order)
                if order:
                    order.status = "refunded"
                    order.save()
                
    except Exception as e:
        print(str(e))
    time.sleep(1.5)
