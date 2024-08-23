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
    """
    Steps in detail:
    - The function first retrieves the current categories from the first row of the sheet and counts them.
    - If there are already 10 categories, it informs the user and exits.
    - Otherwise, it informs the user how many categories have been entered and how many more can be added.
    - It then enters a loop where the user is prompted to input categories separated by commas.
    - The input is split into a list of categories, and any extra whitespace around them is removed.
    - The `validation` function is called to ensure the input is valid.
    - If the input is valid, it updates the sheet with the new categories and exits the loop.
    - If the input is not valid, it informs the user and prompts for input again.
    """
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
    """
    Validates the list of new categories entered by the user.
    
    Parameters:
    - values: List of new categories entered by the user.
    - existing_count: Number of categories already present.
    
    Returns:
    - True if validation passes.
    - False and prints an error message if validation fails.
    """
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
    """
    Prepares a list of budget categories with numbering for display in the terminal menu.
    
    Parameters:
    - data: List of categories or budget data.
    
    Returns:
    - A list of strings formatted with numbering for each category.
    """
    options = [f"{i + 1}. {', '.join(row)}" for i, row in enumerate(data)]
    return options
    

def start():
    """
    Initiates the process to input budget categories.
    """
    categories()  

def budget():
    """
    Allows the user to select a category and input a budget amount, storing the value in the corresponding cell (A1-A10) in the Google Sheet.
    The budget amount will overwrite the category name in the A column.
    """
    categories = sheet1.row_values(1)
    
    if not categories or all(category == "" for category in categories):
        print("No categories available. Please start by entering your budget categories.")
        return
    
    while True:
        # Display the menu of categories
        terminal_menu = TerminalMenu(categories)
        menu_entry_index = terminal_menu.show()
        
        # Get the selected category
        selected_category = categories[menu_entry_index]
        
        # Prompt the user to input the budget for the selected category
        while True:
            try:
                budget_input = float(input(f"Enter your budget for {selected_category}: "))
                sheet1.update_cell(menu_entry_index + 1, 1, budget_input)  # Update the cell in the 'A' column
                print(f"Budget for {selected_category} has been updated to {budget_input}.")
                break
            except ValueError:
                print("Invalid input. Please enter a numerical value.")
        
        # Ask if the user wants to update another category
        continue_input = input("Do you want to update another category? (yes/no): ").strip().lower()
        if continue_input != "yes":
            break



def exit_program():
    """
    Handles the exit operation of the program.
    """
    print("Exiting the program. Goodbye!")

from simple_term_menu import TerminalMenu

def main():
    """
    The main function that presents the user with a menu to navigate different options of the budgeting tool.
    """
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

