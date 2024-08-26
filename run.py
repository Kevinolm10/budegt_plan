import gspread
from google.oauth2.service_account import Credentials

from better_profanity import profanity

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
    """
    - Retrieves categories from column A (A1 to A10) and counts them.
    - If there are 10 categories, it informs the user and exits.
    - Otherwise, it informs the user how many categories have been entered.
    - The user is informed how many more categories can be added.
    - Prompts the user to input categories separated by commas.
    - Splits the input into a list, removing extra whitespace.
    - Calls the `validation` function to check if the input is valid.
    - If valid and free of profanity, updates the sheet and exits.
    - If invalid or contains profanity, it informs the user and prompts again.
    """

    profanity.load_censor_words()

    existing_categories = first_budget.col_values(1)
    existing_categories = [
        category for category in existing_categories 
        if category and category != 'Total'
        ]
    existing_count = len(existing_categories)

    if existing_count >= 10:
        print(f"""
        You have already entered the maximum number of categories (10)."""
        )
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
            category.strip() 
            for category in categories_input.split(',') if category.strip()
            ]

        if any(profanity.contains_profanity(category) 
        for category in category_list):
            print(f"""
            Your input contains inappropriate language. 
            Please enter valid categories.
            """)
            continue

        all_categories = existing_categories + category_list
        unique_categories = list(dict.fromkeys(all_categories))
        unique_categories = unique_categories[:10]

        if validation(unique_categories, existing_count):
            print("Categories are valid! You can proceed with your budgeting.")

            values = [[unique_categories[i]] 
            if i < len(unique_categories) else [""] for i in range(10)]
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
and the total would be {total_count} (excluding the total row)."""
            )
        return True
    except ValueError as e:
        print(f"Invalid data: {e}, please try again\n")
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
    - Allows the user to select a category and input a budget amount.
    - Stores the value in the corresponding cell in the Google Sheet.
    - The budget amount is stored in the B column of the selected category's row.
    - Adds a "Total" row in column A and calculates the total sum in the worksheet.
    """
    row_range = first_budget.range('A1:A10')
    categories = [
        cell.value for cell in row_range 
        if cell.value and cell.value != "Total"
        ]

    if not categories:
        print(f"""
        No categories available. 
        Please start by entering your budget categories.""")
        return

    while True:
        terminal_menu = TerminalMenu(categories)
        menu_entry_index = terminal_menu.show()

        selected_category = categories[menu_entry_index]
        row_index = menu_entry_index + 1

        print("Current categories and their budgets:")
        for i, category in enumerate(categories, start=1):
            current_budget = first_budget.cell(i, 2).value
            print(f"""
            {i}. {category}: {current_budget if current_budget else 
            'No budget set'}
            """)

        while True:
            try:
                budget_input = float(input(f"""
                Enter your budget for {selected_category}:
                """))
                first_budget.update_cell(row_index, 2, budget_input)
                print(f"""
                Budget for {selected_category} has been updated to {
                    budget_input
                    }.
                """)
                break
            except ValueError:
                print("Invalid input. Please enter a numerical value.")

        continue_input = input(f"""
        Do you want to update another category? (yes/no): 
        """).strip().lower()
        if continue_input != "yes":
            break

    total_row = len(categories) + 1
    first_budget.update_cell(total_row, 1, "Total")
    first_budget.update_cell(total_row, 2, f'=SUM(B1:B{len(categories)})')


def total():
    """
    Displays all budget data in a formatted table,
    using Tabulate.
    """
    data = first_budget.get_all_values()

    if not data or all(not row for row in data):
        print("No data available.")
        return

    headers = ["Categories", "Amount"]
    table = tabulate(data, headers=headers, tablefmt="grid")
    print(table)

    input("Press Enter to return to the main menu...")


def remove():
    """
    Allows the user to remove a category from the budget table.
    The selected category's row will be deleted from the sheet.
    """
    row_range = first_budget.range('A1:A10')
    categories = [cell.value for cell in row_range if cell.value and cell.value != "Total"]

    if not categories:
        print("No categories available to remove.")
        return

    while True:
        print("Select a category to remove:")
        terminal_menu = TerminalMenu(categories)
        menu_entry_index = terminal_menu.show()

        selected_category = categories[menu_entry_index]
        row_index = menu_entry_index + 1

        confirmation = input(f"""
        Are you sure you want to remove the category '{selected_category}'? 
        (yes/no): 
        """).strip().lower()

        if confirmation == "yes":
            first_budget.delete_rows(row_index)
            print(f"Category '{selected_category}' has been removed from the budget table.")
            break
        else:
            print("No category was removed.")
            break



def exit_program():
    """ Handles the exit operation of the program. """
    print("Exiting the program. Goodbye!")


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

print(welcome_msg)

print(f"""
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
        print(f"You have selected: {options[menu_options_index]}")

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