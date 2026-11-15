# Personal Finance Manager

A Python-based desktop application for recording and organizing personal financial transactions. It uses MySQL to store transaction data, Tkinter for the graphical interface, and Matplotlib to visualize financial information.

## Features

- **Transaction Management:** Record income, expenses, and savings.
- **Transaction Details:** Store the date, category, description, payment method, gross amount, tax, and net amount.
- **Automatic Net Amount Calculation:** Calculate the net amount based on transaction type and the entered tax percentage.
- **MySQL Database Integration:** Store transactions in a structured relational database.
- **Automatic Database Setup:** Create the database and required tables if they do not already exist.
- **Transaction History:** View recorded transactions in a table through the desktop interface.
- **Expense Distribution Chart:** Visualize expenses grouped by category using a pie chart.
- **Financial Distribution Chart:** Compare the distribution of income, expenses, and savings using a pie chart.
- **Input Validation:** Validate gross amounts and tax inputs before saving transactions.
- **Command-Line Menu:** View database tables, inspect their contents, launch the GUI, and delete transactions.
- **Relational Data Management:** Maintain transaction details across four linked database tables.

## Tech Stack

- **Language:** Python
- **GUI:** Tkinter and ttk
- **Database:** MySQL
- **Database Connector:** mysql-connector-python
- **Data Visualization:** Matplotlib

## Prerequisites

Make sure you have the following installed:

- Python 3
- MySQL Server
- pip (Python package installer)

## Installation and Setup

1. Clone the repository:

   ```bash
   git clone YOUR_REPOSITORY_URL
   cd YOUR_REPOSITORY_FOLDER
   ```

2. Install the required Python packages:

   ```bash
   pip install mysql-connector-python matplotlib
   ```

3. Start your MySQL Server.

4. Configure your MySQL connection credentials in the Python source code. Use environment variables or a local configuration file for sensitive credentials.

5. Run the application:

   ```bash
   python "CS PROJECT ( FINAL ).py"
   ```

The application creates the `finance_manager` database and its required tables when the MySQL connection is successful.

## Database Structure

The application uses four tables:

| Table | Purpose |
|---|---|
| `transaction_desc` | Stores complete transaction details |
| `transaction_summary` | Stores summary information for transactions |
| `trans_classification` | Stores transaction categories and classifications |
| `net_trans` | Stores transaction types, payment methods, and net amounts |

The linked tables use transaction IDs to associate records. Deleting a transaction from the main table is configured to cascade to its linked records.

## Project Purpose

This project demonstrates the use of Python GUI programming, relational database management, SQL queries, input validation, and basic financial data visualization in a desktop application.

## Future Improvements

- Add transaction editing and filtering.
- Generate monthly and yearly financial reports.
- Add date-range-based analysis.
- Improve database credential management.
- Add automated backups and data export.


