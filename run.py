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
*       Welcome to the Budget Planner!          *
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
    print("Please start by entering your budget categories. Separated by commas.")
    print("Example: Travel, Lifestyle, Misc\n")
    
    while True:
        categories_input = input(

            f"Enter your categories of choice here:\n"
            
            )
        category_list = [category.strip() for category in categories_input.split(',')]
        
        if validation(category_list, existing_count):
            print("Categories are valid! You can proceed with your budgeting.")
            
            sheet1.append_row(category_list[:remaining_slots])  
            print("Categories have been added to the sheet.")
            break  

def validation(values, existing_count):
    try:
        total_count = len(values) + existing_count
        if len(values) < 3 or total_count > 10:
            raise ValueError(
                f"Minimum 3 and maximum 10 categories allowed, you have provided {len(values)} "
                f"and the total would be {total_count}"
            )
        return True
    except ValueError as e:
        print(f"Invalid data: {e}, please try again\n")
        return False

def start():
    categories()  

def budget():
    print("Opening budgeting by category...")

def exit_program():
    print("Exiting the program. Goodbye!")

from simple_term_menu import TerminalMenu

def main():
    options = [
        "1. Input your budget categories", 
        "2. Input your budget in each category", 
        "3. Exit"
    ]
    
    terminal_menu = TerminalMenu(options)
    
    while True:
        menu_entry_index = terminal_menu.show()
        print(f"You have selected {options[menu_entry_index]}!")
        
        if menu_entry_index == 0:
            start()
        elif menu_entry_index == 1:
            budget()
        elif menu_entry_index == 2:
            exit_program()
            break

if __name__ == "__main__":
    main()

