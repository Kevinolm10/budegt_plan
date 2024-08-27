import gspread
from google.oauth2.service_account import Credentials

from better_profanity import profanity

from colorama import Fore, Style, init

from tabulate import tabulate

from simple_term_menu import TerminalMenu

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


def categories():
    profanity.load_censor_words()

    existing_categories = first_budget.col_values(1)
    existing_categories = [
        category for category in existing_categories 
        if category and category != 'Total'
    ]
    existing_count = len(existing_categories)

    if existing_count >= 10:
        print(Fore.YELLOW + f"""
        You have already entered the maximum number of categories (10).
        Please refer to option 4 and remove one or more categories.
        """)
        return

    remaining_slots = 10 - existing_count
    print(Fore.GREEN + f"""
Starting your budget journey...

You have already entered {existing_count} categories.

You can add {remaining_slots} more categories.

Please proceed by entering your budget categories reflecting your saving goals,
all separated by commas.

Example: Travel, Lifestyle, Misc
    """)

    while True:
        categories_input = input(Fore.BLUE + f"""
        Enter your categories of choice here 
        or type 'back' to return to the main menu:\n
            """)
        
        if categories_input.lower() == "back":
            return 

        category_list = [
            category.strip() 
            for category in categories_input.split(',') if category.strip()
        ]

        if any(profanity.contains_profanity(category) 
        for category in category_list):
            print(Fore.RED + f"""
            Your input contains inappropriate language. 
            Please enter valid categories.
            """)
            continue

        all_categories = existing_categories + category_list
        unique_categories = list(dict.fromkeys(all_categories))
        total_categories = len(unique_categories)

        if validation(
            new_categories=category_list,
            existing_count=existing_count, 
            total_categories=total_categories
            ):
            print(Fore.GREEN + f"""
            Categories are valid! 
            You can proceed with your budgeting.
            """)

            values = first_budget.range('A1:A10')
            update_values = []
            category_index = 0

            for cell in values:
                if cell.value == "" and category_index < len(category_list):
                    cell.value = category_list[category_index]
                    update_values.append(cell)
                    category_index += 1

            if update_values:
                first_budget.update_cells(update_values)
                print(Fore.GREEN + "Categories have been added to the sheet.")
            else:
                print(Fore.RED + "No space left to add new categories.")
            break




def validation(new_categories, existing_count, total_categories):
    """
    Validates the list of new categories entered by the user.

    Parameters:
    - new_categories: List of new categories entered by the user.
    - existing_count: Number of categories already present.
    - total_categories: Total number of categories including the new ones.

    Returns:
    - True if validation passes.
    - False and prints an error message if validation fails.
    """
    try:
        if total_categories > 10:
            raise ValueError(Fore.RED + f"""
    Maximum 10 categories allowed; you have provided {len(new_categories)}"
    and the total would be {total_categories} (excluding the total row)."
            """)
        return True
    except ValueError as e:
        print(Fore.RED + f"Invalid data: {e}, please try again\n")
        return False



def individual_budget(data):
    """
    Prepares a list of budget categories with
    numbering for display in the terminal menu.

    Parameters:
    - data: List of categories or budget data.

    Returns:
    - A list of strings formatted with numbering for each category.
    """
    options = [f"{i + 1}. {', '.join(row)}" for i, row in enumerate(data)]
    return budget


def budget():
    """
    Allows the user to select a category and input a budget amount.
    Stores the value in the corresponding cell in the Google Sheet.
    The budget is stored in column B of the selected category.
    Adds a "Total" row in column A and calculates the total sum in the sheet.
    """
    row_range = first_budget.range('A1:A10')
    categories = [
        cell.value for cell in row_range 
        if cell.value and cell.value != "Total"
    ]

    if not categories:
        print(Fore.YELLOW + f"""
        No categories available. 
        Please start by entering your budget categories.
        """)
        return

    while True:
        terminal_menu = TerminalMenu(
            categories + ["Back to Main Menu"]
        )
        menu_entry_index = terminal_menu.show()

        if menu_entry_index == len(categories):
            return

        selected_category = categories[menu_entry_index]
        row_index = menu_entry_index + 1

        print(Fore.BLUE + "Current categories and their budgets:")
        for i, category in enumerate(categories, start=1):
            current_budget = first_budget.cell(i, 2).value
            print(f"""
            {i}. {category}: {current_budget if current_budget else Fore.YELLOW + 'No budget set'}
            """)

        while True:
            budget_input = input(Fore.BLUE + f"""
                Enter your budget for {selected_category} (or type 'back' to return to the main menu):
            """)

            if budget_input.lower() == "back":
                return

            try:
                budget_input = float(budget_input)
                first_budget.update_cell(row_index, 2, budget_input)
                print(f"""
                Budget for {selected_category} has been updated to {budget_input}.
                """)
                break
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a numerical value or type 'back' to return to the main menu.")
            
        continue_input = input(Fore.YELLOW + f"""
Do you want to update another category? (yes/no or 'back' to return to the main menu): 
        """).strip().lower()

        if continue_input == "back" or continue_input != "yes":
            break

    total_row = None
    for i, cell in enumerate(first_budget.col_values(1), start=1):
        if cell.lower() == "total":
            total_row = i
            break

    if not total_row:
        total_row = len(categories) + 1
        first_budget.update_cell(total_row, 1, "Total")

    last_row = len(categories)
    total_formula = f'=SUM(B1:B{last_row})'
    first_budget.update_cell(total_row, 2, total_formula)

    print(Fore.GREEN + f"""
The total budget has been updated. 
You can view the total at the bottom of the categories in your Google Sheet.
""")


def total():
    """
    Displays all budget data in a formatted table,
    using Tabulate.
    """
    data = first_budget.get_all_values()

    if not data or all(not row for row in data):
        print(Fore.RED + "No data available.")
        return

    headers = ["Categories", "Amount"]
    table = tabulate(data, headers=headers, tablefmt="grid")
    print(table)

    input(Fore.BLUE + "Press Enter to return to the main menu or type 'back' to go back:")
    return


def remove():
    """
    Allows the user to remove a category from the budget table.
    The selected category's row will be deleted from the sheet.
    """
    row_range = first_budget.range('A1:A10')
    categories = [
        cell.value for cell in row_range 
        if cell.value and cell.value != "Total"
    ]

    if not categories:
        print(Fore.RED + "No categories available to remove.")
        return

    while True:
        terminal_menu = TerminalMenu(categories + ["Back to Main Menu"])
        menu_entry_index = terminal_menu.show()

        if menu_entry_index == len(categories):
            return

        selected_category = categories[menu_entry_index]
        row_index = menu_entry_index + 1

        confirmation = input(Fore.YELLOW + f"""
Are you sure you want to remove the category '{selected_category}'? 
(yes/no or 'back' to return to the main menu): 
        """).strip().lower()

        if confirmation == "back":
            return

        if confirmation == "yes":
            first_budget.delete_rows(row_index)
            print(Fore.RED + f"""
            Category '{selected_category}' 
            has been removed from the budget table.
            """)
            break
        else:
            print(Fore.YELLOW + "No category was removed.")
            break


def exit_program():
    """ Handles the exit operation of the program. """
    print(Fore.BLUE + "Exiting the program. Goodbye!")


def main():
    """
    The main function that presents the user with a menu to navigate different
    options of the budgeting tool.
    """

welcome_msg = """
*************************************************
*                                               *
*          Welcome to the Budget Planner!       *
*        Your way to find economical peace      *
*                                               *
*************************************************
"""

print(Fore.GREEN + welcome_msg)

print(Fore.YELLOW + f"""
Select menu options 1 through 3 to start managing your budget.

option 1 is for selecting categories to be put in the budget table(option 3).
option 2 if for putting the amount of money into each individual category.
option 3 is for viewing the contents of the table you have created.
""")

options = [
    "1. Input your budget categories",
    "2. Input amount in each category",
    "3. View your total budget table",
    "4. Remove categories in the budget table",
    "5. Close"
]

terminal_menu = TerminalMenu(options)

while True:
        menu_options_index = terminal_menu.show()
        print(Fore.BLUE + f"You have selected: {options[menu_options_index]}")

        if menu_options_index == 0:
            categories()
        elif menu_options_index == 1:
            budget()
        elif menu_options_index == 2:
            total()
        elif menu_options_index == 3:
            remove()
        elif menu_options_index == 4:
            exit_program()
            break


if __name__ == "__main__":
    main()