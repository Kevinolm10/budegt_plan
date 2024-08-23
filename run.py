import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('budget_planner')


sheet1 = SHEET.worksheet('sheet1')

data = sheet1.get_all_values()


welcome_msg = """
*************************************************
*                                               *
*          Welcome to the Budget Planner!       * 
*        Your way to find economical peace      *
*                                               *
*************************************************
"""

print(welcome_msg)

def categories():
    existing_categories = sheet1.row_values(1) 
    existing_count = len(existing_categories) 

    if existing_count >= 10:
        print("You have already entered the maximum number of categories (10).")
        return

    print("Starting your budget journey...\n")
    print(f"You have already entered {existing_count} categories.")
    remaining_slots = 10 - existing_count
    print(f"You can add {remaining_slots} more categories.")
    print("Please start by entering your budget categories, separated by commas.")
    print("Example: Travel, Lifestyle, Misc\n")
    
    while True:
        categories_input = input("Enter your categories of choice here:\n")
        category_list = [category.strip() for category in categories_input.split(',')]
        
        if validation(category_list, existing_count):
            print("Categories are valid! You can proceed with your budgeting.")
            values = [[category_list[i]] if i < len(category_list) else [""] for i in range(10)]
            sheet1.update(range_name='A1:A10', values=values)
            
            print("Categories have been added to the sheet.")
            break

def validation(values, existing_count):
    try:
        total_count = len(values) + existing_count
        if len(values) < 3 or total_count > 10:
            raise ValueError(
                f"Minimum 3 and maximum 10 categories allowed; you have provided {len(values)} "
                f"and the total would be {total_count}"
            )
        return True
    except ValueError as e:
        print(f"Invalid data: {e}, please try again\n")
        return False

def individual_budget(data):
    options = [f"{i + 1}. {', '.join(row)}" for i, row in enumerate(data)]
    return options
    

def start():
    categories()  

def budget():
    options = individual_budget(data)
    if options:
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        print(f"You have selected: {options[menu_entry_index]}")
    else:
        raise ValueError (
            f"No budget data available to display." 
            f"Please refer back to option 1 in the main menu"
        )


def exit_program():
    print("Exiting the program. Goodbye!")

from simple_term_menu import TerminalMenu

def main():
    options = [
        "1. Input your budget categories", 
        "2. View your budget in each category",
        "3. View your total budget table", 
        "4. Close"
    ]
    
    terminal_menu = TerminalMenu(options)
    
    while True:
        categories_index = terminal_menu.show()
        print(f"You have selected: {options[categories_index]}")
        
        if categories_index == 0:
            start()
        elif categories_index == 1:
            budget()
        elif categories_index == 2:
            total()
        elif categories_index == 3:
            exit_program()
            break

if __name__ == "__main__":
    main()

