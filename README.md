# FreshMart – Grocery Store Management System

FreshMart is a web-based Grocery Store Management System developed using Python Flask, MySQL, HTML, CSS and JavaScript. It helps supermarket owners manage products, maintain inventory, generate customer bills and monitor store sales.

## Features

### 1. Product Management
- Add new products with name, price, unit and stock quantity.
- View all available products.
- Edit existing product details.
- Delete products.
- Search products and navigate through paginated results.

### 2. Inventory Management
- Maintain product stock quantities.
- Automatically update stock after successful billing.
- Prevent billing when the requested quantity exceeds available stock.
- Identify low-stock and out-of-stock products.

### 3. Billing System
- Generate customer bills.
- Calculate product subtotals and total bill amount.
- Save order information and order details in MySQL.
- Automatically deduct sold quantities from inventory.

### 4. Order Management
- View previous orders.
- Check individual order details.
- Track customer names, order dates and total amounts.

### 5. Store Insights
- View today's, weekly and monthly sales.
- Monitor total orders and average order value.
- Visualize weekly sales through a chart.
- View total products, low-stock products and out-of-stock products.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| MySQL | Database management |
| HTML | Page structure |
| CSS | Styling and layout |
| JavaScript | Frontend interactions |
| mysql-connector-python | MySQL connectivity |
| python-dotenv | Environment variable management |

## Project Structure

```text
grocery_store/
│
├── app.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
│
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── manage_products.html
│   ├── view_products.html
│   ├── edit_product.html
│   ├── billing.html
│   ├── order_history.html
│   ├── order_details.html
│   └── store_insights.html
│
└── venv/
```

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- MySQL Server
- MySQL Workbench
- Visual Studio Code

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd grocery_store
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the MySQL Database

- Open MySQL Workbench.
- Create a database named `grocery_store`.
- Create the required tables: `products`, `uom`, `orders` and `order_details`.
- Configure the primary keys, foreign keys and required columns according to the project database structure.

### 5. Configure Environment Variables

Create a `.env` file in the project root directory:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=grocery_store
```

Replace `your_mysql_password` with your own MySQL password.

### 6. Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## Learning Outcomes

Through this project, I gained practical experience with:

- Building web applications using Flask.
- Connecting Python applications to MySQL.
- Performing database CRUD operations.
- Implementing inventory and billing workflows.
- Handling database transactions and stock validation.
- Creating sales reports and dashboard visualizations.
- Managing application configuration using environment variables.

## Future Enhancements

- Printable customer invoices.
- User authentication and role-based access.
- Advanced sales reports and inventory analytics.

---

**Project:** FreshMart – Grocery Store Management System  
**Category:** Full-Stack Web Application  
**Status:** sCore features implemented and tested locally.
