# Importing FastAPI framework
from fastapi import FastAPI

# It Creates FastAPI application object
app = FastAPI()

# Sample data to stored in a list of dictionaries
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Office Chair", "price": 3999, "category": "Furniture", "in_stock": False},

    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]

# API 1: Get all products
@app.get("/products")
def get_products():
     # It will return full product list and total count
    return {"products": products, "total": len(products)}

# API 2: Get products by category
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    # Filter products
    result = [p for p in products if p["category"] == category_name]

    # If no product found
    if not result:
        return {"error": "No products found in this category"}

    # Return filtered products
    return {"category": category_name, "products": result, "total": len(result)}

# API 3: Get only products that are in stock
@app.get("/products/instock")
def get_instock():
    # Filter products
    available = [p for p in products if p["in_stock"] == True]
    return {"in_stock_products": available, "count": len(available)}

# API 4: Store information
@app.get("/store/summary")
def store_summary():
    # Count products that are in stock
    in_stock_count = len([p for p in products if p["in_stock"]])

    # Count products which are out of stock
    out_stock_count = len(products) - in_stock_count

    # This Gives unique product categories
    categories = list(set([p["category"] for p in products]))

    # Returns information
    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories,
    }

# API 5: Search product by keyword
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
     # Search product names based on the keyword
    results = [p for p in products if keyword.lower() in p["name"].lower()]

    # If no match found
    if not results:
        return {"message": "No products matched your search"}

    return {"keyword": keyword, "results": results, "total_matches": len(results)}

# API 6: Get best deal and most expensive product
@app.get("/products/deals")
def get_deals():
     # Find product with lowest price
    cheapest = min(products, key=lambda p: p["price"])

     # Find product with highest price
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive,
    }
