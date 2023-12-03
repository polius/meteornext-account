import time
import stripe

# Testing
stripe.api_key = ""
# Production
# stripe.api_key = ""

def calculate_price(resources):
    max_price_x_server = 10
    max_price_reduction = 8.5
    max_servers = 500
    price_x_server = max_price_x_server
    if (resources > 10): price_x_server = max_price_x_server - (((max_price_x_server - max_price_reduction) / max_servers) * resources)
    new_price = price_x_server * resources
    return new_price

products = []
prices = []

for i in range(5,501):
    name = f"Meteor Next - {i} Servers"
    price = int(calculate_price(i)*100)
    print(name + ' | ' + str(price))

    while True:
        try:
            stripe_product = stripe.Product.create(name=name, images=['https://www.meteornext.io/assets/logo.png'])
            break
        except Exception:
            time.sleep(1)

    while True:
        try:
            stripe_price = stripe.Price.create(
                unit_amount=price,
                currency="eur",
                recurring={"interval": "month"},
                tax_behavior="exclusive",
                product=stripe_product['id'],
            )
            break
        except Exception:
            time.sleep(1)

    products.append({"name": name, "resources": i, "stripe_id": stripe_product['id']})
    prices.append({"price": price, "product_id": stripe_product['id'], "stripe_id": stripe_price['id']})


with open('stripe_products.txt', 'w') as fopen:
    # Compute products
    sql = "INSERT INTO `products` (`name`, `resources`, `stripe_id`)\nVALUES"
    sql += "\n('Meteor Next - Unlimited Servers','-1',NULL),"
    sql += "\n('Meteor Next - 1 Server','1',NULL),"
    for p in products:
        sql += f"\n('{p['name']}','{p['resources']}','{p['stripe_id']}'),"
    sql = sql[:-1] + ';\n\n'

    # Compute prices
    sql += "INSERT INTO `prices` (`price`, `product_id`, `stripe_id`, `is_default`)\nVALUES"
    for p in prices:
        sql += f"\n('{int(p['price'])/100}',(SELECT id FROM products WHERE stripe_id = '{p['product_id']}'),'{p['stripe_id']}', 1),"
    sql = sql[:-1] + ';\n'
    
    # Write SQLs to file
    fopen.write(sql)
