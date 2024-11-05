import pickle
from collections import defaultdict
from broodcode_modules.menu_props import get_max_widths, format_row, format_separator, print_header

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
        with open(f"./pickles/{filename}.pickle", "rb") as file:
            data = pickle.load(file)
    except FileNotFoundError:
        return False
    return data

def calculate_sandwiches():
    opened_pickles = [open_pickle("sandwich"), open_pickle("panini"), open_pickle("special")]

    print("COPY BLOCK")

    profit_sandwiches = None
    profit_paninis = None
    profit_specials = None

    for pickle in opened_pickles:
        if pickle is False:
            print("You haven´t fetched the menu yet. Do that first before you try to calculate the amount of sandwiches")
            return
    try:
        with open("order.txt") as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(
            "Create order.txt, with a single code per line, or delete the pickles for a new order round"
        )
        return
    
    for index, pickle in enumerate(opened_pickles):
        messages = ["Freshly topped sandwiches", "Paninis", "Special of the Week"]
        print_pickle(lines, pickle, messages[index])

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