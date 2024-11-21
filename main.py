from broodcode_modules.broodcode import menu
from broodcode_modules.calculate_sandwiches import calculate_sandwiches

APP_VERSION = "2.0.0"

# For future features below...
# Option 3 will say which sandwiches doesn´t contain these ingredients
# Option 4 will show a help menu
# The exit() will be replaced from option 3 to option 5

def main():
    print(f"Welcome to the broodcode mass order system version { APP_VERSION } Please select one of the following options")
    while True:
        print("""
            1. Show the menu
            2. Calculate ordered sandwiches
            3. Exit
            """)
        while True:
            try:
                option = int(input("Make your choice: "))
                if option:
                    break
            except ValueError:
                print("That is not a number, Just type a number")

        match option:
            case 1:
                menu()
            case 2:
                calculate_sandwiches() # calculate the sandwiches in this option
            case 3:
                exit() # request the sandwich ingredients in this option
            case _:
                print("This number does not have an available option. please try another one")

main()