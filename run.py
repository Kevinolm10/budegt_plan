import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('65756f82816a0ab6936ac9d578c800e607bc85fe')
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

    print("Starting your budget journey...")
    print("Please start by entering your budget categories. Min 3 and max 10, separated by commas.")
    print("Exampel: Travel, Lifestyle, Misc")
    print(f"""
    hifoiqefhqefuhoqefh

dofofadodpfoadpf
    """)
    while True:
        categories = input("Enter your categories of choice here: ")
        category_list = [category.strip() for category in categories.split(',')]
        
        if validation(category_list):
            print("Categories are valid! You can proceed with your budgeting.")
            sheet1.append_row(category_list)
            print("Categories have been added to the sheet.")
            break  
        else:
            print("Invalid input. Please try again.\n")

def validation(values):
    
    if len(values) < 3 or len(values) > 10:
        print(f"Minimum 3 and maximum 10 categories required, you have provided {len(values)}")
        return False

    return True

def show_menu():

    print("=== Main Menu ===")
    print("1. Input your budget categories")
    print("2. Input your budget in each category")
    print("3. Exit")
    print("=================\n")

def start():
    categories()  

def budget():
    print("Opening budgeting by category...")

def exit_program():
    print("Exiting the program. Goodbye!")

def main():
    while True:
        show_menu()
        choice = input("Please choose an option (1-3): ")

        if choice == '1':
            start()
        elif choice == '2':
            budget()
        elif choice == '3':
            exit_program()
            break
        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()

