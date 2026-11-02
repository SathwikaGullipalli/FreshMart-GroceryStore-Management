
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
from mysql.connector import Error, IntegrityError
import math
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# Get all available units
def get_units(cursor):
    cursor.execute(
        "SELECT uom_id, uom_name FROM uom ORDER BY uom_id"
    )
    return cursor.fetchall()


# Get all products
def get_products(cursor):
    cursor.execute("""
        SELECT p.product_id, p.name, p.uom_id,
               p.price_per_unit, u.uom_name
        FROM products p
        LEFT JOIN uom u ON p.uom_id = u.uom_id
        ORDER BY p.product_id DESC
    """)
    return cursor.fetchall()


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Manage Products: add products
@app.route("/manage-products", methods=["GET", "POST"])
def manage_products():
    connection = None
    cursor = None

    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()

        try:
            unit_id = int(request.form.get("unit", ""))
            price = float(request.form.get("price", ""))
            stock_quantity = float(request.form.get("stock_quantity", ""))

            if not product_name:
                flash("Please enter a product name.", "error")
                return redirect(url_for("manage_products"))

            if price <= 0 or not math.isfinite(price):
                flash("Price must be a valid number greater than zero.", "error")
                return redirect(url_for("manage_products"))
            
            if stock_quantity < 0 or not math.isfinite(stock_quantity):
               flash("Stock quantity must be a valid number greater than or equal to zero.", "error")
               return redirect(url_for("manage_products"))


            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT uom_id FROM uom WHERE uom_id = %s",
                (unit_id,)
            )

            if cursor.fetchone() is None:
                flash("Please select a valid unit.", "error")
            else:
                
                cursor.execute("""
                INSERT INTO products (name, uom_id, price_per_unit, stock_quantity)
                VALUES (%s, %s, %s, %s)
                """, (product_name, unit_id, price, stock_quantity))


                connection.commit()
                flash("Product added successfully!", "success")

        except ValueError:
            flash("Please enter a valid unit and price.", "error")

        except Error as error:
            flash(f"Database error: {error}", "error")

        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

        return redirect(url_for("manage_products"))

    # Load the add-product page
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        units = get_units(cursor)

        cursor.execute("SELECT COUNT(*) AS total FROM products")
        product_count = cursor.fetchone()["total"]

        return render_template(
            "manage_products.html",
            units=units,
            product_count=product_count
        )

    except Error as error:
        flash(f"Could not load the page: {error}", "error")
        return render_template(
            "manage_products.html",
            units=[],
            product_count=0
        )

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# View All Products: search and pagination
@app.route("/view-products")
def view_products():
    connection = None
    cursor = None

    search = request.args.get("q", "").strip()

    try:
        page = int(request.args.get("page", 1))
    except ValueError:
        page = 1

    page = max(page, 1)

    per_page = 10
    offset = (page - 1) * per_page

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Count products matching the search
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM products
            WHERE name LIKE %s
        """, (f"%{search}%",))

        total_products = cursor.fetchone()["total"]
        total_pages = max(1, math.ceil(total_products / per_page))

        # Keep requested page within valid limits
        page = min(page, total_pages)
        offset = (page - 1) * per_page

        # Get products for the current page
        cursor.execute("""
            SELECT p.product_id, p.name, p.price_per_unit,
               p.stock_quantity, u.uom_name
            FROM products p
            LEFT JOIN uom u ON p.uom_id = u.uom_id
            WHERE p.name LIKE %s
            ORDER BY p.product_id DESC
            LIMIT %s OFFSET %s
        """, (f"%{search}%", per_page, offset))

        products = cursor.fetchall()

        return render_template(
            "view_products.html",
            products=products,
            search=search,
            page=page,
            per_page=per_page,
            total_products=total_products,
            total_pages=total_pages
        )

    except Error as error:
        flash(f"Could not load products: {error}", "error")
        return render_template(
            "view_products.html",
            products=[],
            search=search,
            page=1,
            per_page=per_page,
            total_products=0,
            total_pages=1
        )

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()



# Edit a product
@app.route("/edit-product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT product_id, name, uom_id, price_per_unit,
                   stock_quantity
            FROM products
            WHERE product_id = %s
        """, (product_id,))

        product = cursor.fetchone()

        if not product:
            flash("Product not found.", "error")
            return redirect(url_for("view_products"))

        units = get_units(cursor)

        if request.method == "POST":
            product_name = request.form.get(
                "product_name", ""
            ).strip()

            try:
                unit_id = int(request.form.get("unit", ""))
                price = float(request.form.get("price", ""))
                stock_quantity = float(
                    request.form.get("stock_quantity", "")
                )

                valid_unit_ids = [
                    unit["uom_id"] for unit in units
                ]

                if not product_name:
                    flash(
                        "Product name cannot be empty.",
                        "error"
                    )

                elif not math.isfinite(price) or price <= 0:
                    flash(
                        "Price must be a valid number greater than zero.",
                        "error"
                    )

                elif (
                    not math.isfinite(stock_quantity)
                    or stock_quantity < 0
                ):
                    flash(
                        "Stock must be a valid number greater than or equal to zero.",
                        "error"
                    )

                elif unit_id not in valid_unit_ids:
                    flash(
                        "Please select a valid unit.",
                        "error"
                    )

                else:
                    cursor.execute("""
                        UPDATE products
                        SET name = %s,
                            uom_id = %s,
                            price_per_unit = %s,
                            stock_quantity = %s
                        WHERE product_id = %s
                    """, (
                        product_name,
                        unit_id,
                        price,
                        stock_quantity,
                        product_id
                    ))

                    connection.commit()

                    flash(
                        "Product updated successfully!",
                        "success"
                    )

                    return redirect(url_for("view_products"))

            except ValueError:
                flash(
                    "Please enter valid values for unit, price and stock.",
                    "error"
                )

        return render_template(
            "edit_product.html",
            product=product,
            units=units
        )

    except Error:
        app.logger.exception("Could not edit product")
        flash(
            "A database error occurred while editing the product.",
            "error"
        )
        return redirect(url_for("view_products"))

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()



# Delete a product
@app.route("/delete-product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM products WHERE product_id = %s",
            (product_id,)
        )

        if cursor.rowcount > 0:
            connection.commit()
            flash("Product deleted successfully!", "success")
        else:
            flash("Product not found.", "error")

    except IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()

        flash(
            "This product is linked to an existing order and cannot be deleted.",
            "error"
        )

    except Error as error:
        if connection and connection.is_connected():
            connection.rollback()

        flash(f"Could not delete product: {error}", "error")

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

    return redirect(url_for("view_products"))


@app.route("/billing")
def billing():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT product_id, name, price_per_unit
            FROM products
            ORDER BY name
        """)

        products = cursor.fetchall()

        return render_template(
            "billing.html",
            products=products
        )

    except Error as error:
        flash(f"Could not load billing page: {error}", "error")
        return redirect(url_for("home"))

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# Order History: display all saved bills
@app.route("/order-history")
def order_history():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT order_id, customer_name, total, date_time
            FROM orders
            ORDER BY date_time DESC, order_id DESC
        """)

        orders = cursor.fetchall()

        return render_template(
            "order_history.html",
            orders=orders
        )

    except Error as error:
        app.logger.exception("Could not load order history")
        flash("Could not load order history. Please try again.", "error")
        return redirect(url_for("home"))

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# View details of one order
@app.route("/order-details/<int:order_id>")
def order_details(order_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get the main order information
        cursor.execute("""
            SELECT order_id, customer_name, total, date_time
            FROM orders
            WHERE order_id = %s
        """, (order_id,))

        order = cursor.fetchone()

        # If the order does not exist, return to Order History
        if not order:
            flash("Order not found.", "error")
            return redirect(url_for("order_history"))

        # Get all products included in this order
        cursor.execute("""
            SELECT p.name, p.price_per_unit, u.uom_name,
                   od.quantity, od.total_price
            FROM order_details od
            JOIN products p ON od.product_id = p.product_id
            LEFT JOIN uom u ON p.uom_id = u.uom_id
            WHERE od.order_id = %s
            ORDER BY p.name
        """, (order_id,))

        items = cursor.fetchall()

        return render_template(
            "order_details.html",
            order=order,
            items=items
        )

    except Error:
        app.logger.exception("Could not load order details")
        flash("Could not load order details. Please try again.", "error")
        return redirect(url_for("order_history"))

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# Store Insights
@app.route("/store-insights")
def store_insights():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                COALESCE(SUM(CASE
                    WHEN DATE(date_time) = CURDATE()
                    THEN total ELSE 0 END), 0) AS today_sales,

                COALESCE(SUM(CASE
                    WHEN YEARWEEK(date_time, 1) = YEARWEEK(CURDATE(), 1)
                    THEN total ELSE 0 END), 0) AS weekly_sales,

                COALESCE(SUM(CASE
                    WHEN YEAR(date_time) = YEAR(CURDATE())
                    AND MONTH(date_time) = MONTH(CURDATE())
                    THEN total ELSE 0 END), 0) AS monthly_sales,

                COUNT(*) AS total_orders,

                COALESCE(AVG(total), 0) AS average_order_value

            FROM orders
        """)

        insights = cursor.fetchone()
                # Inventory Summary
        cursor.execute("""
            SELECT
                COUNT(*) AS total_products,

                SUM(CASE
                    WHEN stock_quantity > 0
                    AND stock_quantity <= 5
                    THEN 1 ELSE 0
                END) AS low_stock_products,

                SUM(CASE
                    WHEN stock_quantity <= 0
                    THEN 1 ELSE 0
                END) AS out_of_stock_products

            FROM products
        """)

        inventory_summary = cursor.fetchone()
        
        cursor.execute("""
            SELECT
              WEEKDAY(date_time) AS day_order,
              DAYNAME(date_time) AS day_name,
              SUM(total) AS daily_sales
            FROM orders
            WHERE YEARWEEK(date_time, 1) = YEARWEEK(CURDATE(), 1)
            GROUP BY WEEKDAY(date_time), DAYNAME(date_time)
            ORDER BY day_order
        """)

        weekly_sales_data = cursor.fetchall()
        weekly_max_sales = max(
               (float(day["daily_sales"]) for day in weekly_sales_data),
               default=1
        )
        if weekly_max_sales == 0:
             weekly_max_sales = 1
        for day in weekly_sales_data:
            day["bar_height"] = max(
                4,
                int(float(day["daily_sales"]) / weekly_max_sales * 200)
            )


        weekly_max_sales = max(weekly_max_sales, 1)


        return render_template(
            "store_insights.html",
            insights=insights,
            weekly_sales_data=weekly_sales_data,
            weekly_max_sales=weekly_max_sales,
            inventory_summary=inventory_summary
        )

    except Error:
        app.logger.exception("Could not load store insights")
        flash("Could not load Store Insights. Please try again.", "error")
        return redirect(url_for("home"))

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()






# Save a bill to MySQL
@app.route("/save-bill", methods=["POST"])
def save_bill():
    connection = None
    cursor = None

    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "message": "Invalid bill data."}), 400

        customer_name = data.get("customer_name", "")
        items = data.get("items")

        if not isinstance(customer_name, str):
            return jsonify({"success": False, "message": "Invalid customer name."}), 400
        customer_name = customer_name.strip()
        if not customer_name or len(customer_name) > 100:
            return jsonify({"success": False, "message": "Enter a customer name of up to 100 characters."}), 400
        if not isinstance(items, list) or not items:
            return jsonify({"success": False, "message": "Add at least one product."}), 400

        quantities = {}
        for item in items:
            if not isinstance(item, dict):
                return jsonify({"success": False, "message": "Invalid product information."}), 400
            product_id = item.get("product_id")
            quantity = item.get("quantity")
            if isinstance(product_id, bool) or not isinstance(product_id, int) or product_id <= 0:
                return jsonify({"success": False, "message": "Invalid product ID."}), 400
            if (isinstance(quantity, bool) or not isinstance(quantity, (int, float))
                    or not math.isfinite(quantity) or quantity <= 0):
                return jsonify({"success": False, "message": "Every quantity must be greater than zero."}), 400
            quantities[product_id] = quantities.get(product_id, 0) + quantity
            if not math.isfinite(quantities[product_id]):
                return jsonify({"success": False, "message": "Invalid quantity total."}), 400

        connection = get_db_connection()
        connection.start_transaction()
        cursor = connection.cursor()

        product_ids = list(quantities.keys())
        placeholders = ", ".join(["%s"] * len(product_ids))
        cursor.execute(
            f"""SELECT product_id, name, price_per_unit, stock_quantity
            FROM products
            WHERE product_id IN ({placeholders})
            FOR UPDATE""",
            tuple(product_ids)
        )
        
        products = cursor.fetchall()
        products_by_id = {row[0]: row for row in products}

        if len(products_by_id) != len(product_ids):
            connection.rollback()
            return jsonify({"success": False, "message": "A selected product no longer exists."}), 400

        order_items = []
        grand_total = 0.0
        for product_id, quantity in quantities.items():
            product = products_by_id[product_id]
            price = float(product[2])
            available_stock = float(product[3])

            if not math.isfinite(available_stock) or available_stock < 0:
                    connection.rollback()
                    return jsonify({
                       "success": False,
                       "message": f"Invalid stock quantity for {product[1]}."
                    }), 400

            if quantity > available_stock:
              connection.rollback()
              return jsonify({
                  "success": False,
                   "message": f"Not enough stock for {product[1]}. Available: {available_stock}"
                }), 400
            if not math.isfinite(price) or price < 0:
                connection.rollback()
                return jsonify({"success": False, "message": "A product has an invalid price."}), 400
            subtotal = round(price * quantity, 2)
            if not math.isfinite(subtotal):
                connection.rollback()
                return jsonify({"success": False, "message": "Bill amount is too large."}), 400
            grand_total += subtotal
            order_items.append((product_id, quantity, subtotal))

        grand_total = round(grand_total, 2)
        if not math.isfinite(grand_total):
            connection.rollback()
            return jsonify({"success": False, "message": "Invalid bill total."}), 400

        cursor.execute(
            "INSERT INTO orders (customer_name, total, date_time) VALUES (%s, %s, NOW())",
            (customer_name, grand_total)
        )
        order_id = cursor.lastrowid
        cursor.executemany(
            "INSERT INTO order_details (order_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
            [(order_id, product_id, quantity, subtotal)
             for product_id, quantity, subtotal in order_items]
        )
        # Deduct purchased quantities from available stock
        for product_id, quantity, subtotal in order_items:
            cursor.execute(
                """UPDATE products
                   SET stock_quantity = stock_quantity - %s
                   WHERE product_id = %s AND stock_quantity >= %s""",
                (quantity, product_id, quantity)
            )

            if cursor.rowcount != 1:
                connection.rollback()
                return jsonify({
                    "success": False,
                    "message": "Stock could not be updated. Please try again."
                }), 400
        connection.commit()
        return jsonify({
            "success": True,
            "message": f"Bill saved successfully! Order ID: {order_id}",
            "order_id": order_id,
            "total": grand_total
        })

    except (ValueError, TypeError, OverflowError):
        if connection and connection.is_connected():
            connection.rollback()
        return jsonify({"success": False, "message": "Invalid bill information."}), 400
    except Error:
        if connection and connection.is_connected():
            connection.rollback()
        app.logger.exception("Could not save bill")
        return jsonify({"success": False, "message": "Could not save the bill. Please check the database and try again."}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


# Test database connection
@app.route("/test-db")
def test_db():
    connection = None

    try:
        connection = get_db_connection()
        return "Database connection successful!"

    except Error as error:
        return f"Database connection failed: {error}"

    finally:
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(debug=True)
