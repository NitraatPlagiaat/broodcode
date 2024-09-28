
import json
import requests
import pickle
from datetime import date
from collections import defaultdict

codes = {}
versions = []

def calculate_price(bread_type, totals, product):
    org_price = price = round(product["price"]*100 + bread_type["surcharge"]*100)
    while price in codes:
        price += 1
    profit = price - org_price
    totals["profit"] += profit
    totals["count"] += 1

    codes[price] = (product['title'], bread_type['name'], profit)
    versions.append(f"{bread_type['name'].lower()}={price}")

    return {"profit": totals["profit"], "count": totals["count"]}

def fetch_menu():
    response = requests.get(f'https://bestellen.broodbode.nl/v2-2/pccheck/null/{date.today()}/afhalen/8?cb=1695969466297', headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0'})

    data = response.json()
    products = data["products"]
    bread_types_by_id = {b["id"]: b for b in data["breadtypes"]}

    return {"products": products, "breadtypes": bread_types_by_id}

def build_sandwich_menu():

    totals = {"profit": 0, "count": 0}

    bread = fetch_menu()

    for product in sorted(bread["products"], key = lambda product: product["price"]):
        if not product["breadtypes"]:
            continue
        compatible_bread_type_ids = json.loads(product["breadtypes"])
        if 41 not in compatible_bread_type_ids: # Only regular sandwiches
            continue

        versions.clear()

        for bread_type_id in compatible_bread_type_ids:
            if bread_type_id in bread["breadtypes"]:
                totals = calculate_price(bread["breadtypes"][bread_type_id], totals, product)

        print(f"{product['title']}: {' '.join(versions)}")

    with open('data.pickle', 'wb') as file:
        pickle.dump({'products': bread["products"], 'codes': codes}, file)

    print(f"Average profit: {round(totals['profit']/totals['count'])} cents per sandwich")

def print_pickle(lines, data):
    totals = {"profit": 0, "count": 0}
    orders = defaultdict(lambda: defaultdict(int))

    for line in lines:
        title, bread_type, profit = data["codes"][int(line)]
        orders[title][bread_type] += 1
        totals["profit"] += profit
        totals["count"] += 1

    for product in data["products"]:
        o = orders.get(product["title"])
        if o:
            amounts = " ".join(f"{k.lower()}={v}" for k,v in sorted(o.items()))
            print(f"{product['title'].split(':')[0].strip()}: {amounts}")

    print(f"\n{totals['count']} sandwiches. {totals['profit']} cents profit!")

def main():
    try:
        with open('data.pickle', 'rb') as file:
            data = pickle.load(file)
    except FileNotFoundError:
        build_sandwich_menu()
    else:
        try:
            with open('order.txt') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]
        except FileNotFoundError:
            print("Create order.txt, with a single code per line, or delete data.pickle for a new order round")
            exit(1)

        print_pickle(lines, data)

        exit()

main()