import json
import pickle
from datetime import date
from collections import defaultdict

import requests

APP_VERSION = "1.2.1"

codes = {}
versions = []


def get_max_widths(rows):
    """Calculate maximum column width based on longest string in each column."""
    return [max(len(str(item)) for item in col) for col in zip(*rows, strict=False)]


def format_row(row_items, col_widths):
    """Format a row with variable column width based on longest content."""
    return (
        "|"
        + "|".join(f"{str(item):<{col_widths[i]}}" for i, item in enumerate(row_items))
        + "|"
    )


def format_separator(col_widths):
    """Create a separator row based on column widths for Markdown table."""
    return "|" + "|".join("-" * col_width for col_width in col_widths) + "|"


def print_header(title):
    print(f"## {title}\n")


def calculate_price(bread_type, totals, product):
    org_price = price = round(product["price"] * 100 + bread_type["surcharge"] * 100)
    while price in codes:
        price += 1
    profit = price - org_price
    totals["profit"] += profit
    totals["count"] += 1

    codes[price] = (product["title"], bread_type["name"], profit)
    versions.append(f"{bread_type['name'].lower()}={price}")

    return {
        "profit": totals["profit"],
        "count": totals["count"],
        "product": codes[price],
        "price": price,
    }


def fetch_menu():
    try:
        response = requests.get(
            f"https://bestellen.broodbode.nl/v2-2/pccheck/null/{date.today()}/afhalen/8?cb=1695969466297",
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0"
            },
            timeout=10,  # Timeout after 10 seconds
        )
    except requests.exceptions.Timeout:
        print("The request timed out. Please try again later.")
        return {"products": [], "breadtypes": {}}
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return {"products": [], "breadtypes": {}}

    data = response.json()
    products = data["products"]
    bread_types_by_id = {b["id"]: b for b in data["breadtypes"]}

    return {"products": products, "breadtypes": bread_types_by_id}


def build_sandwich_menu():
    totals = {"profit": 0, "count": 0}
    codes_sandwiches = {}

    menu = fetch_menu()

    print_header("Freshly topped sandwiches")

    # Prepare data for table rows
    rows = [["Sandwich", "White", "Grain", "Foca", "Spelt", "G-Free"]]

    for product in sorted(menu["products"], key=lambda product: product["price"]):
        if not product["breadtypes"]:
            continue
        if "special van de week" in product["title"].lower():
            continue  # Skip 'Special van de week'
        compatible_bread_type_ids = json.loads(product["breadtypes"])
        if 41 not in compatible_bread_type_ids:
            continue

        versions.clear()
        compatible_bread_type_ids.sort()

        # Initialize row with sandwich name
        row = [product["title"].strip()]

        bread_type_ids = [41, 42, 43, 44, 45]
        for bread_type_id in bread_type_ids:  # IDs for White, Grain, Focaccia, Spelt, Gluten-Free
            if (
                bread_type_id in compatible_bread_type_ids
                and bread_type_id in menu["breadtypes"]
            ):
                prices = calculate_price(
                    menu["breadtypes"][bread_type_id], totals, product
                )
                codes_sandwiches[prices["price"]] = prices["product"]
                row.append(str(prices["price"]))
            else:
                row.append("-")

        # Add row to rows list
        rows.append(row)

    col_widths = get_max_widths(
        rows
    )  # Calculate column widths based on max string length in each column

    # Print the table
    print("```")
    print(format_row(rows[0], col_widths))  # Print header row
    print(format_separator(col_widths))  # Print separator
    for row in rows[1:]:
        print(format_row(row, col_widths))  # Print data rows
    print("```\n")

    with open("sandwich.pickle", "wb") as file:
        pickle.dump({"products": menu["products"], "codes": codes_sandwiches}, file)

    return round(totals["profit"] / totals["count"])


def build_special_menu():
    totals = {"profit": 0, "count": 0}
    codes_specials = {}

    menu = fetch_menu()

    print_header("Special of the Week")

    for product in sorted(menu["products"], key=lambda product: product["price"]):
        if not product["breadtypes"]:
            continue
        if "special" not in product["title"].lower():
            continue

        compatible_bread_type_ids = json.loads(product["breadtypes"])
        versions.clear()

        # Remove the "Special van de week" prefix
        title = (
            product["title"]
            .replace("Special van de week : ", "")
            .replace(".", "")
            .strip()
        )

        # Initialize row for the special menu
        row = []
        bread_type_ids = [41, 42, 43, 44, 45]
        for bread_type_id in bread_type_ids:  # IDs for White, Grain, Focaccia, Spelt, Gluten-Free
            if (
                bread_type_id in compatible_bread_type_ids
                and bread_type_id in menu["breadtypes"]
            ):
                prices = calculate_price(
                    menu["breadtypes"][bread_type_id], totals, product
                )
                codes_specials[prices["price"]] = prices["product"]
                row.append(str(prices["price"]))
            else:
                row.append("-")

        # Only print the special title if we found a valid special
        if row:
            print(title)  # Print the special title
            # Prepare data for the Markdown table
            rows = [["Bread Type", "Price"]]
            for bread_type_id in [41, 42, 43, 44, 45]:
                bread_name = menu["breadtypes"][bread_type_id]["name"].title()
                price = row[bread_type_id - 41]  # Adjust for zero-indexing in the array
                rows.append([bread_name, price])

            col_widths = get_max_widths(
                rows
            )  # Calculate column widths based on max string length in each column

            # Print the table
            print("```")
            print(format_row(rows[0], col_widths))  # Print header row
            print(format_separator(col_widths))  # Print separator
            for r in rows[1:]:
                print(format_row(r, col_widths))  # Print data rows
            print("```\n")

    with open("special.pickle", "wb") as file:
        pickle.dump({"products": menu["products"], "codes": codes_specials}, file)

    return round(totals["profit"] / totals["count"])


def build_paninis_menu():
    totals = {"profit": 0, "count": 0}
    codes_paninis = {}

    menu = fetch_menu()

    print_header("Panini's")

    # Prepare data for table rows
    rows = [["Panini", "Focaccia"]]

    for product in sorted(menu["products"], key=lambda product: product["price"]):
        compatible_bread_type_ids = json.loads(product["breadtypes"])
        if product["categorie_id"] != 71:
            continue

        versions.clear()

        # Initialize row with panini name
        row = [product["title"].strip()]

        if (
            43 in compatible_bread_type_ids and 43 in menu["breadtypes"]
        ):  # ID for Focaccia
            prices = calculate_price(menu["breadtypes"][43], totals, product)
            codes_paninis[prices["price"]] = prices["product"]
            row.append(str(prices["price"]))
        else:
            row.append("-")

        # Add row to rows list
        rows.append(row)

    col_widths = get_max_widths(
        rows
    )  # Calculate column widths based on max string length in each column

    # Print the table
    print("```")
    print(format_row(rows[0], col_widths))  # Print header row
    print(format_separator(col_widths))  # Print separator
    for row in rows[1:]:
        print(format_row(row, col_widths))  # Print data rows
    print("```\n")

    with open("panini.pickle", "wb") as file:
        pickle.dump({"products": menu["products"], "codes": codes_paninis}, file)

    return round(totals["profit"] / totals["count"])


def print_pickle(lines, data, header):
    totals = {"profit": 0, "count": 0}
    orders = defaultdict(lambda: defaultdict(int))

    print_header(header)

    # Prepare data for table rows
    rows = [["Sandwich", "Type", "Quantity"]]

    for line in lines:
        if int(line) in data["codes"]:
            title, bread_type, profit = data["codes"][int(line)]
            orders[title][bread_type] += 1
            totals["profit"] += profit
            totals["count"] += 1

    for product in data["products"]:
        o = orders.get(product["title"])
        if o:
            for bread_type, quantity in sorted(o.items()):
                # Add row to rows list
                rows.append(
                    [
                        product["title"].split(":")[0].strip(),
                        bread_type.lower(),
                        quantity,
                    ]
                )

    col_widths = get_max_widths(
        rows
    )  # Calculate column widths based on max string length in each column

    # Print the table
    print(format_row(rows[0], col_widths))  # Print header row
    print(format_separator(col_widths))  # Print separator
    for row in rows[1:]:
        print(format_row(row, col_widths))  # Print data rows

    print(f"\n{totals['count']} sandwiches. {totals['profit']} cents profit!")
    print("")


def open_pickle(filename):
    try:
        with open(f"{filename}.pickle", "rb") as file:
            data = pickle.load(file)
    except FileNotFoundError:
        return False
    return data


def menu():
    sandwich_pickle = open_pickle("sandwich")
    panini_pickle = open_pickle("panini")
    special_pickle = open_pickle("special")

    print("COPY BLOCK")

    profit_sandwiches = None
    profit_paninis = None
    profit_specials = None
    if special_pickle is False:
        profit_specials = build_special_menu()
    if sandwich_pickle is False:
        profit_sandwiches = build_sandwich_menu()
    if panini_pickle is False:
        profit_paninis = build_paninis_menu()
    else:
        try:
            with open("order.txt") as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]
        except FileNotFoundError:
            print(
                "Create order.txt, with a single code per line, or delete data.pickle for a new order round"
            )
            exit(1)

        print_pickle(lines, sandwich_pickle, "Freshly topped sandwiches")
        print_pickle(lines, panini_pickle, "Paninis")
        print_pickle(lines, special_pickle, "Special of the Week")

        print("Don't forget to copy the sentence below to put in the notes on the order summary screen:")
        print("'Graag, als dit mogelijk is, de broodsoorten op de zakken schrijven b.v.d.'")

        exit()

    print("/COPY BLOCK")
    print()

    if profit_sandwiches:
        print(f"Average sandwich profit: {profit_sandwiches} cents per sandwich")
    if profit_paninis:
        print(f"Average panini profit: {profit_paninis} cents per panini")
    if profit_specials:
        print(f"Average special profit: {profit_specials} cents per special")


if __name__ == "__main__":
    menu()
