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
SHEET = GSPREAD_CLIENT.open('budget_plan')


first_budget = SHEET.worksheet('first_budget')

data = first_budget.get_all_values()


welcome_msg = """
*************************************************
*                                               *
*          Welcome to the Budget Planner!       * 
*        Your way to find economical peace      *
*                                               *
*************************************************
"""

print(welcome_msg)

from better_profanity import profanity

def categories():
    """
    - The function first retrieves the current categories from the first row of the sheet and counts them.
    - If there are already 10 categories, it informs the user and exits.
    - Otherwise, it informs the user how many categories have been entered and how many more can be added.
    - It then enters a loop where the user is prompted to input categories separated by commas.
    - The input is split into a list of categories, and any extra whitespace around them is removed.
    - The `validation` function is called to ensure the input is valid.
    - If the input is valid and free of profanity, it updates the sheet with the new categories and exits the loop.
    - If the input is not valid or contains profanity, it informs the user and prompts for input again.
    """

    profanity.load_censor_words()

    existing_categories = first_budget.row_values(1)
    existing_count = len(existing_categories)

    if existing_count >= 10:
        print("You have already entered the maximum number of categories (10).")
        return

    remaining_slots = 10 - existing_count
    print(f"""
Starting your budget journey...

You have already entered {existing_count} categories.
You can add {remaining_slots} more categories.
Please start by entering your budget categories, separated by commas.
Example: Travel, Lifestyle, Misc

    """)

    while True:
        categories_input = input("Enter your categories of choice here:\n")
        category_list = [
            category.strip() for category in categories_input.split(',')
        ]
        if any(profanity.contains_profanity(category) for category in category_list):
            print(f"""
Your input contains inappropriate language. Please enter valid categories.
                    """)
            continue

        if validation(category_list, existing_count):
            print("Categories are valid! You can proceed with your budgeting.")
            values = [
                [category_list[i]] if i < len(category_list) else [""] for i in range(10)
            ]
            first_budget.update(range_name='A1:A10', values=values)
            
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
                f"""
Minimum 3 and maximum 10 categories allowed; you have provided {len(values)} 
and the total would be {total_count}"""
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
    return budget


def budget():
    """
    Allows the user to select a category and input a budget amount, storing the value in the corresponding cell in the Google Sheet.
    The budget amount will be stored in the B column of the selected category's row.
    It also adds a "Total" row in column A and calculates the total sum of the budget in the worksheet.
    """
    categories = first_budget.range('A1:A10')
    
    categories = [cell.value for cell in categories if cell.value]

    if not categories:
        print(f"""
        No categories available. Please start by entering your budget categories.
        """)
        return

    while True:
        terminal_menu = TerminalMenu(categories)
        menu_entry_index = terminal_menu.show()
        
        selected_category = categories[menu_entry_index]
        row_index = menu_entry_index + 1  
        print("Current categories and their budgets:")
        for i, category in enumerate(categories, start=1):
            current_budget = first_budget.cell(i, 2).value
            print(
                f"{i}. {category}: {
                    current_budget if current_budget else 'No budget set'
                }"
            )
        
        while True:
            try:
                budget_input = float(input(
                    f"""
Enter your budget for {selected_category}:
                """))
                first_budget.update_cell(row_index, 2, budget_input) 
                print(
                    f"""
Budget for {selected_category} has been updated to 
{budget_input}."""
                    )
                break
            except ValueError:
                print("Invalid input. Please enter a numerical value.")
        
        total_row = len(categories) + 2  
        first_budget.update_cell(total_row, 1, "Total")  
        first_budget.update_cell(total_row, 2, f'=SUM(B1:B{len(categories)})')  
        
        continue_input = input(f"""
Do you want to update another category? (yes/no): 
""").strip().lower()
        if continue_input != "yes":
            break

from tabulate import tabulate

def total():
    """
    Displays all budget data in a formatted table,
    using Tabulate.
    """
    data = first_budget.get_all_values()
    
    if not data or all(not row for row in data):
        print("No data available.")
        return

    table = tabulate(data, headers="firstrow", tablefmt="grid")
    print(table)

    input("Press Enter to return to the main menu...")


def exit_program():
    """ Handles the exit operation of the program. """
    print("Exiting the program. Goodbye!")


from simple_term_menu import TerminalMenu

def main():
    """
    The main function that presents the user with a menu to navigate different
    options of the budgeting tool.
    """
    options = [
        "1. Input your budget categories", 
        "2. Input amount of money in each category",
        "3. View your total budget table", 
        "4. Close"
    ]
    
    terminal_menu = TerminalMenu(options)
    
    while True:
        categories_index = terminal_menu.show()
        print(f"You have selected: {options[categories_index]}")
        
        if categories_index == 0:
            categories()
        elif categories_index == 1:
            budget()
        elif categories_index == 2:
            total()
        elif categories_index == 3:
            exit_program()
            break

if __name__ == "__main__":
    main()

