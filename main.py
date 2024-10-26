from broodcode_modules.broodcode import menu

def main():
    print("Welcome to the broodcode mass order system. Please select one of the following options")
    while True:
        print("""
            1. Show the menu
            2. Calculate ordered sandwiches
            3. Request sandwich ingredients
            4. Help
            5. exit
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
                pass # calculate the sandwishes in this option
            case 3:
                pass # request the sandwich ingredients in this option
            case 4:
                pass # Help info here
            case 5:
                exit()
            case _:
                print("This number does not have an available option. please try another one")

main()