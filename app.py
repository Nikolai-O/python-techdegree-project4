import csv, datetime, os
from collections import OrderedDict
from decimal import Decimal
from peewee import *

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = AutoField()
    product_name = CharField(unique=True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

def create_inventory():
    with open('inventory.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for line in csv_reader:
            line['product_price'] = int(float(line['product_price'].strip("$")) * 100)
            line['product_quantity'] = int(line['product_quantity'])
            line['date_updated'] = datetime.datetime.strptime(line['date_updated'], "%m/%d/%Y")

            try:
                Product.create(product_name=line['product_name'],
                           product_price=line['product_price'],
                           product_quantity=line['product_quantity'],
                           date_updated=line['date_updated'])

            except IntegrityError:
                product_record = Product.get(product_name=line['product_name'])
                if product_record.date_updated < line['date_updated']:
                    product_record.product_name = line['product_name']
                    product_record.product_price = line['product_price']
                    product_record.product_quantity = line['product_quantity']
                    product_record.date_updated = line['date_updated']
                    product_record.save()
                else:
                    continue

def menu_loop():
    choice = None

    while choice != 'q':
        print("Enter 'q' to quit.")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input('Selection: ').lower().strip()
        while choice not in menu:
            if choice == 'q':
                break
            choice = input("Please enter a valid selection(a, v, b or q): ")

        if choice in menu:
            menu[choice]()
    clear()        

def view_products():
    """View products in inventory"""
    min_id = (Product.select().order_by(Product.product_id.asc()).get()).product_id
    max_id = (Product.select().order_by(Product.product_id.desc()).get()).product_id
    print(f"\nPlease select id between {min_id} & {max_id}")
    id = int(input("Select product id: "))
    while id not in range(min_id, max_id+1):
        print("Your selection must be between {} and {}".format(min_id, max_id))
        id = int(input("Select product id: "))
    print(f"""\n-Product: {Product.get_by_id(id).product_name}
-Quantity: {Product.get_by_id(id).product_quantity}
-Price: {Product.get_by_id(id).product_price} cents
-Date updated: {Product.get_by_id(id).date_updated}\n""")
    input("\nPress ENTER to continue")
    clear()

def add_product():
    """Add a new product to the inventory"""
    name = input("\nPlease enter the name of the new product: ")
    quantity = int(input("Please enter the quantity of the new product: "))
    price = int(input("Please enter the price of the new product(in dollars): ").strip("$")) * 100

    try:
        Product.create(product_name=name,
                       product_price=price,
                       product_quantity=quantity)
        latest_item = Product.select().order_by(Product.product_id.desc()).get()
        print(f"You just added {latest_item.product_name} as the {latest_item.product_id}th item in the inventory.\n")

    except IntegrityError:
        to_update = Product.get(product_name=name)
        to_update.product_name = name
        to_update.product_price = price
        to_update.product_quantity = quantity
        to_update.date_updated = datetime.datetime.now()
        to_update.save()
        print(f"You just updated {to_update.product_name}\n")
    input("\nPress ENTER to continue")
    clear()


def create_backup():
    """Creates a backup of the inventory"""
    with open('inventory_backup.csv', 'a') as csvfile:
        fieldnames = ['product_name', 'product_price', 'product_quantity', 'date_updated']
        backupwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        backupwriter.writeheader()
        for item in Product.select():
            backupwriter.writerow({
            'product_name': item.product_name,
            'product_price': round(Decimal(item.product_price / 100), 2),
            'product_quantity': item.product_quantity,
            'date_updated': item.date_updated.strftime("%m/%d/%Y")
            })
        print("\nBackup created!\n")
    input("\nPress ENTER to continue")
    clear()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def initialize():
    db.connect()
    db.create_tables([Product])
    create_inventory()

menu = OrderedDict([
    ('v', view_products),
    ('a', add_product),
    ('b', create_backup)
])

if __name__ == "__main__":
    initialize()
    menu_loop()
