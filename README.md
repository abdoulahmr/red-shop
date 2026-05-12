# RedShop Documentation

## 1. Project Overview
RedShop is a lightweight e-commerce web application built with Flask. It allows users to browse products, search for items, and place orders. It includes an admin panel for managing inventory (products), handling images, and processing orders.

**Tech Stack:**
*   **Backend:** Flask (Python)
*   **Database:** SQLite (via SQLAlchemy)
*   **Authentication:** Flask-Login
*   **File Storage:** Local filesystem (`static/uploads`)

---

## 2. Installation & Setup

### Prerequisites
*   Python 3.7+
*   pip (Python package installer)

### Step 1: Install Dependencies
Create a virtual environment (optional but recommended) and install the required packages:

```bash
pip install -r requirements.txt
```

### Step 2: Initialize the Database
Since you are using SQLite, you must create the database file and tables before running the app.

Run this script once:
```bash
python init_db.py
```

This will generate a file named `redshop.db`.

### Step 3: Run the Application
```bash
python app.py
```
The app will typically run at `http://127.0.0.1:5000/`.

---

## 3. Configuration (`config.py`)

The application configuration is centralized in the `Config` class.

*   **Database:** `sqlite:///redshop.db`
*   **Debug Mode:** `True` (Enabled for development)
*   **Upload Folder:** `static/uploads` (Ensure this directory exists)
*   **Secret Key:** Used for session management 
*   **Allowed Extensions:** `{'svg', 'png', 'jpg', 'jpeg'}`

---

## 4. Database Models (`models.py`)

The application uses SQLAlchemy ORM with three main concepts:

### User (Authentication)
*   **Type:** Custom Class (Non-database model)
*   **Description:** Handles user sessions for the Admin panel.
*   **Storage:** Uses a hardcoded dictionary `users = {'admin': {'password': 'admin'}}`.
*   **Default Credentials:**
    *   Username: `admin`
    *   Password: `admin`

### Product
*   **Table:** `products`
*   **Columns:**
    *   `id` (Integer, PK)
    *   `title` (String)
    *   `description` (Text)
    *   `quantity` (Integer)
    *   `price` (Float)
    *   `image` (String) - Stores the filename of the uploaded image.

### Order
*   **Table:** `orders`
*   **Columns:**
    *   `id` (Integer, PK)
    *   `product_id` (Integer, FK) - Links to `products.id`
    *   `first_name`, `last_name`, `address`, `phone_number`
    *   `quantity` (Integer)
    *   `status` (String) - Default: 'pending'
    *   `note` (Text)
    *   `date_time` (DateTime)

---

## 5. Routes & Functionality (`app.py`)

### Public Routes (No Login Required)

| Route | Method | Description |
| :--- | :--- | :--- |
| `/` | GET | **Home Page.** Displays a list of all available products. |
| `/product:<id>` | GET | **Product Detail.** Shows specific product details. |
| `/product:<id>` | POST | **Place Order.** Captures form data (Name, Address, Phone, Quantity) and creates a new `Order` record linked to the product ID. |
| `/search` | GET | **Search.** Filters products by title (Case-insensitive). |

### Authentication Routes

| Route | Method | Description |
| :--- | :--- | :--- |
| `/admin/login` | GET | Renders the login form. |
| `/admin/login` | POST | Authenticates user against the `users` dictionary. |
| `/logout` | GET | Logs the current user out and redirects to home. |

### Admin Routes (Login Required)

*All routes in this section are protected by `@login_required`. Redirects to login if not authenticated.*

| Route | Method | Description |
| :--- | :--- | :--- |
| `/admin/dashboard` | GET | **Dashboard.** Main landing page for the admin. |
| `/admin/product` | GET | **Inventory List.** Displays all products. |
| `/admin/product` | POST | **Add Product.** Accepts product details and an image file. <br> *Logic:* Validates file type, saves image to `static/uploads` with a timestamp prefix, and saves record to DB. |
| `/admin/edit_product/<id>` | GET | Renders edit form for a specific product. |
| `/admin/edit_product/<id>` | POST | **Update Product.** Updates product details. <br> *Logic:* If a new image is uploaded, the old image is deleted from the filesystem, and the new one is saved. |
| `/admin/delete_product/<id>` | GET | **Delete Product.** Removes the product from the DB and deletes the associated image file from the server. |
| `/admin/orders` | GET | **Order List.** Displays all orders joined with product titles. Shows customer info, status, and order details. |
| `/admin/update_order/<id>` | POST | **Update Status.** Changes the order status (e.g., from 'pending' to 'shipped'). |
| `/admin/delete_order/<id>` | POST | **Delete Order.** Removes an order record from the database. |

---

## 6. API Blueprint (`api.py`)
*Note: The code imports `api_bp` from `api.py`, but the file content was not provided in the prompt. Documentation for API endpoints should be added here once available.*

---

## 7. File Structure Recommendation

```
/redshop
    ├── app.py               # Main application entry point
    ├── config.py            # Configuration settings
    ├── models.py            # Database models
    ├── api.py               # API endpoints (if applicable)
    ├── init_db.py           # Database initialization script
    ├── static/
    │   └── uploads/         # Stores product images
    └── templates/           # HTML files
        ├── home.html
        ├── product_view.html
        ├── admin_login.html
        ├── admin_dashboard.html
        ├── product.html
        ├── edit_product.html
        └── order.html
```