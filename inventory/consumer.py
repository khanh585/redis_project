from main import redis, Product
import time

key_completed = 'order_completed'
key_refunded = 'order_refunded'
group = 'inventory-group'

try:
    redis.xgroup_create(key_completed, group)
except:
    print('Group already exists')

while True:
    try:
        result = redis.xreadgroup(group, key_completed, {key_completed: '>'}, None)
        if result:
            for item in result:
                obj_result = item[1][0][1]
                product = Product.get(obj_result['product_id'])
                print(product)
                if product and product.quantity >= int(obj_result['quantity']):
                    product.quantity = product.quantity - int(obj_result['quantity'])
                    product.save()
                else:
                    redis.xadd(key_refunded, obj_result, '*')
    except Exception as e:
        print(str(e))
    time.sleep(1.5)
