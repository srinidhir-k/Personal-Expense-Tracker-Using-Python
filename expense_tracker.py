import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import calendar
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Wedge
import numpy as np

class ExpenseTracker:
    def __init__(self, data_file='expenses.json'):
        """
        Initialize the ExpenseTracker with data file and predefined categories.
        
        Args:
            data_file (str): Path to JSON file for storing expense data
        """
        self.data_file = data_file
        self.expenses = self.load_data()
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
            'Bills & Utilities', 'Healthcare', 'Education', 'Travel',
            'Groceries', 'Other'
        ]
        
        # Set up matplotlib style for better-looking plots
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
    
    def load_data(self):
        """
        Load expense data from JSON file.
        
        Returns:
            list: List of expense dictionaries, empty list if file doesn't exist
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_data(self):
        """Save expense data to JSON file with proper formatting."""
        with open(self.data_file, 'w') as f:
            json.dump(self.expenses, f, indent=2)
    
    def add_expense(self, amount, description, category, date=None):
        """
        Add a new expense to the tracker.
        
        Args:
            amount (float): Expense amount
            description (str): Description of the expense
            category (str): Category of the expense
            date (str, optional): Date in YYYY-MM-DD format, defaults to today
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        expense = {
            'id': len(self.expenses) + 1,
            'amount': float(amount),
            'description': description,
            'category': category,
            'date': date,
            'timestamp': datetime.now().isoformat()
        }
        
        self.expenses.append(expense)
        self.save_data()
        print(f"✓ Expense added: ${amount} for {description}")
    
    def view_expenses(self, limit=10):
        """
        Display recent expenses in a formatted table.
        
        Args:
            limit (int): Number of recent expenses to display
        """
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        
        print(f"\n--- Recent Expenses (Last {limit}) ---")
        sorted_expenses = sorted(self.expenses, key=lambda x: x['timestamp'], reverse=True)
        
        for expense in sorted_expenses[:limit]:
            print(f"ID: {expense['id']} | ${expense['amount']:.2f} | {expense['category']} | {expense['description']} | {expense['date']}")
    
    def delete_expense(self, expense_id):
        """
        Delete an expense by its ID.
        
        Args:
            expense_id (int): ID of the expense to delete
            
        Returns:
            bool: True if expense was deleted, False if not found
        """
        for i, expense in enumerate(self.expenses):
            if expense['id'] == expense_id:
                deleted = self.expenses.pop(i)
                self.save_data()
                print(f"✓ Deleted expense: ${deleted['amount']:.2f} for {deleted['description']}")
                return True
        print(f"Expense with ID {expense_id} not found.")
        return False
    
    def get_monthly_summary(self, year=None, month=None, show_chart=True):
        """
        Generate monthly expense summary with optional visualization.
        
        Args:
            year (int, optional): Year for summary, defaults to current year
            month (int, optional): Month for summary, defaults to current month
            show_chart (bool): Whether to display pie chart visualization
        """
        if year is None:
            year = datetime.now().year
        if month is None:
            month = datetime.now().month
        
        month_str = f"{year}-{month:02d}"
        monthly_expenses = [e for e in self.expenses if e['date'].startswith(month_str)]
        
        if not monthly_expenses:
            print(f"No expenses found for {calendar.month_name[month]} {year}")
            return
        
        total = sum(e['amount'] for e in monthly_expenses)
        category_totals = defaultdict(float)
        
        for expense in monthly_expenses:
            category_totals[expense['category']] += expense['amount']
        
        print(f"\n--- {calendar.month_name[month]} {year} Summary ---")
        print(f"Total Expenses: ${total:.2f}")
        print(f"Number of Transactions: {len(monthly_expenses)}")
        print(f"Average per Transaction: ${total/len(monthly_expenses):.2f}")
        
        print("\nBy Category:")
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total) * 100
            print(f"  {category}: ${amount:.2f} ({percentage:.1f}%)")
        
        if show_chart and category_totals:
            self.plot_category_pie_chart(category_totals, f"{calendar.month_name[month]} {year}")
    
    def plot_category_pie_chart(self, category_totals, title_suffix=""):
        """
        Create and display a pie chart for category-wise expenses.
        
        Args:
            category_totals (dict): Dictionary with categories as keys and amounts as values
            title_suffix (str): Additional text for chart title
        """
        # Prepare data for pie chart
        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Define colors for different categories
        colors = plt.cm.Set3(np.linspace(0, 1, len(categories)))
        
        # Create pie chart with enhanced styling
        wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%',
                                         colors=colors, startangle=90, 
                                         textprops={'fontsize': 9})
        
        # Enhance the appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(f'Expense Distribution by Category\n{title_suffix}', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Add a legend with amounts
        legend_labels = [f'{cat}: ${amt:.2f}' for cat, amt in category_totals.items()]
        ax.legend(wedges, legend_labels, title="Categories", loc="center left", 
                 bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        plt.show()
    
    def get_category_summary(self, days=30, show_chart=True):
        """
        Generate category-wise spending summary for specified number of days.
        
        Args:
            days (int): Number of days to analyze
            show_chart (bool): Whether to display bar chart visualization
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        recent_expenses = [e for e in self.expenses if e['date'] >= cutoff_str]
        
        if not recent_expenses:
            print(f"No expenses found in the last {days} days.")
            return
        
        category_totals = defaultdict(float)
        for expense in recent_expenses:
            category_totals[expense['category']] += expense['amount']
        
        total = sum(category_totals.values())
        
        print(f"\n--- Category Summary (Last {days} days) ---")
        print(f"Total Spent: ${total:.2f}")
        
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total) * 100
            print(f"{category}: ${amount:.2f} ({percentage:.1f}%)")
        
        if show_chart and category_totals:
            self.plot_category_bar_chart(category_totals, f"Last {days} Days")
    
    def plot_category_bar_chart(self, category_totals, title_suffix=""):
        """
        Create and display a horizontal bar chart for category-wise expenses.
        
        Args:
            category_totals (dict): Dictionary with categories as keys and amounts as values
            title_suffix (str): Additional text for chart title
        """
        # Sort categories by amount for better visualization
        sorted_items = sorted(category_totals.items(), key=lambda x: x[1])
        categories = [item[0] for item in sorted_items]
        amounts = [item[1] for item in sorted_items]
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create horizontal bar chart
        bars = ax.barh(categories, amounts, color=plt.cm.viridis(np.linspace(0, 1, len(categories))))
        
        # Add value labels on bars
        for i, (bar, amount) in enumerate(zip(bars, amounts)):
            ax.text(bar.get_width() + max(amounts) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'${amount:.2f}', va='center', fontweight='bold')
        
        ax.set_xlabel('Amount ($)', fontsize=12, fontweight='bold')
        ax.set_title(f'Expenses by Category - {title_suffix}', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def search_expenses(self, keyword):
        """
        Search for expenses containing a keyword in description or category.
        
        Args:
            keyword (str): Search term to look for
        """
        results = []
        keyword = keyword.lower()
        
        for expense in self.expenses:
            if (keyword in expense['description'].lower() or 
                keyword in expense['category'].lower()):
                results.append(expense)
        
        if not results:
            print(f"No expenses found containing '{keyword}'")
            return
        
        print(f"\n--- Search Results for '{keyword}' ---")
        for expense in sorted(results, key=lambda x: x['date'], reverse=True):
            print(f"ID: {expense['id']} | ${expense['amount']:.2f} | {expense['category']} | {expense['description']} | {expense['date']}")
    
    def get_spending_trends(self, months=6, show_chart=True):
        """
        Analyze and visualize spending trends over time.
        
        Args:
            months (int): Number of months to analyze
            show_chart (bool): Whether to display line chart visualization
        """
        trends = defaultdict(float)
        
        for expense in self.expenses:
            month_key = expense['date'][:7]  # YYYY-MM format
            trends[month_key] += expense['amount']
        
        sorted_months = sorted(trends.keys(), reverse=True)[:months]
        
        print(f"\n--- Spending Trends (Last {months} months) ---")
        for month in reversed(sorted_months):
            year, month_num = month.split('-')
            month_name = calendar.month_name[int(month_num)]
            print(f"{month_name} {year}: ${trends[month]:.2f}")
        
        if show_chart and len(sorted_months) > 1:
            self.plot_spending_trends(trends, months)
    
    def plot_spending_trends(self, trends, months):
        """
        Create and display a line chart showing spending trends over time.
        
        Args:
            trends (dict): Dictionary with month keys and total amounts as values
            months (int): Number of months to display
        """
        # Get last N months of data
        sorted_months = sorted(trends.keys(), reverse=True)[:months]
        sorted_months.reverse()  # Reverse to show chronological order
        
        # Prepare data for plotting
        month_labels = []
        amounts = []
        
        for month in sorted_months:
            year, month_num = month.split('-')
            month_labels.append(f"{calendar.month_name[int(month_num)][:3]} {year}")
            amounts.append(trends[month])
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Create line chart
        line = ax.plot(month_labels, amounts, marker='o', linewidth=2, markersize=8, 
                      color='#2E86AB', markerfacecolor='#A23B72')
        
        # Add value labels on points
        for i, amount in enumerate(amounts):
            ax.annotate(f'${amount:.0f}', (i, amount), textcoords="offset points", 
                       xytext=(0,10), ha='center', fontweight='bold')
        
        ax.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
        ax.set_title('Monthly Spending Trends', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def plot_daily_expenses(self, days=30):
        """
        Create a daily expense visualization for the last N days.
        
        Args:
            days (int): Number of days to visualize
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y-%m-%d')
        
        recent_expenses = [e for e in self.expenses if e['date'] >= cutoff_str]
        
        if not recent_expenses:
            print(f"No expenses found in the last {days} days.")
            return
        
        # Group expenses by date
        daily_totals = defaultdict(float)
        for expense in recent_expenses:
            daily_totals[expense['date']] += expense['amount']
        
        # Create date range for the last N days
        date_range = [(cutoff_date + timedelta(days=i)).strftime('%Y-%m-%d') 
                     for i in range(days + 1)]
        
        # Fill in missing dates with 0
        amounts = [daily_totals.get(date, 0) for date in date_range]
        
        # Convert to datetime objects for plotting
        dates = [datetime.strptime(date, '%Y-%m-%d') for date in date_range]
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Create bar chart
        bars = ax.bar(dates, amounts, color='#F18F01', alpha=0.7, edgecolor='#C73E1D')
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, days//10)))
        
        # Add value labels on bars (only for non-zero values)
        for bar, amount in zip(bars, amounts):
            if amount > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(amounts)*0.01,
                       f'${amount:.0f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
        
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Amount ($)', fontsize=12, fontweight='bold')
        ax.set_title(f'Daily Expenses - Last {days} Days', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    
    def display_menu(self):
        """Display the main menu with all available options."""
        print("\n" + "="*60)
        print("           PERSONAL EXPENSE TRACKER")
        print("="*60)
        print("1. Add Expense")
        print("2. View Recent Expenses")
        print("3. Monthly Summary (with Pie Chart)")
        print("4. Category Summary (with Bar Chart)")
        print("5. Search Expenses")
        print("6. Delete Expense")
        print("7. Spending Trends (with Line Chart)")
        print("8. Daily Expenses Chart")
        print("9. Exit")
        print("="*60)
    
    def run(self):
        """
        Main application loop that handles user interactions.
        This method displays the menu and processes user choices.
        """
        print("Welcome to Personal Expense Tracker with Visualizations!")
        
        while True:
            self.display_menu()
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == '1':
                self.add_expense_interactive()
            elif choice == '2':
                try:
                    limit = int(input("Number of recent expenses to show (default 10): ") or "10")
                    self.view_expenses(limit)
                except ValueError:
                    self.view_expenses()
            elif choice == '3':
                self.monthly_summary_interactive()
            elif choice == '4':
                try:
                    days = int(input("Number of days to analyze (default 30): ") or "30")
                    self.get_category_summary(days)
                except ValueError:
                    self.get_category_summary()
            elif choice == '5':
                keyword = input("Enter search keyword: ").strip()
                if keyword:
                    self.search_expenses(keyword)
            elif choice == '6':
                try:
                    expense_id = int(input("Enter expense ID to delete: "))
                    self.delete_expense(expense_id)
                except ValueError:
                    print("Invalid expense ID.")
            elif choice == '7':
                try:
                    months = int(input("Number of months to analyze (default 6): ") or "6")
                    self.get_spending_trends(months)
                except ValueError:
                    self.get_spending_trends()
            elif choice == '8':
                try:
                    days = int(input("Number of days to visualize (default 30): ") or "30")
                    self.plot_daily_expenses(days)
                except ValueError:
                    self.plot_daily_expenses()
            elif choice == '9':
                print("Thank you for using Personal Expense Tracker!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def add_expense_interactive(self):
        """
        Interactive method for adding expenses with user input validation.
        Guides user through the process of entering expense details.
        """
        try:
            amount = float(input("Enter amount: $"))
            description = input("Enter description: ").strip()
            
            print("\nAvailable Categories:")
            for i, category in enumerate(self.categories, 1):
                print(f"{i}. {category}")
            
            try:
                cat_choice = int(input("Select category (number): "))
                if 1 <= cat_choice <= len(self.categories):
                    category = self.categories[cat_choice - 1]
                else:
                    category = "Other"
            except ValueError:
                category = "Other"
            
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if date_input:
                try:
                    datetime.strptime(date_input, '%Y-%m-%d')
                    self.add_expense(amount, description, category, date_input)
                except ValueError:
                    print("Invalid date format. Using today's date.")
                    self.add_expense(amount, description, category)
            else:
                self.add_expense(amount, description, category)
                
        except ValueError:
            print("Invalid amount. Please enter a valid number.")
    
    def monthly_summary_interactive(self):
        """
        Interactive method for generating monthly summaries.
        Allows user to specify year and month for the summary.
        """
        try:
            year = input(f"Enter year (default {datetime.now().year}): ").strip()
            year = int(year) if year else datetime.now().year
            
            month = input(f"Enter month (1-12, default {datetime.now().month}): ").strip()
            month = int(month) if month else datetime.now().month
            
            if 1 <= month <= 12:
                self.get_monthly_summary(year, month)
            else:
                print("Invalid month. Please enter a number between 1 and 12.")
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

def main():
    """
    Main function to run the expense tracker application.
    This is the entry point of the program.
    """
    try:
        tracker = ExpenseTracker()
        tracker.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please check your input and try again.")

if __name__ == "__main__":
    main()
