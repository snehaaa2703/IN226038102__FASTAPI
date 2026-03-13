from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field

app = FastAPI()

# Pydantic models
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

class NewProduct(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    in_stock: bool = True


# Data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
]

orders = []
order_counter = 1


# Helper functions
def find_product(product_id: int):
    """Search product by ID."""
    for p in products:
        if p["id"] == product_id:
            return p
    return None


def calculate_total(product: dict, quantity: int) -> int:
    """Multiply price by quantity."""
    return product["price"] * quantity


def filter_products_logic(category=None, min_price=None, max_price=None, in_stock=None):
    """Apply filters."""
    result = products

    if category is not None:
        result = [p for p in result if p["category"] == category]

    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return result


# Endpoints

# Day 1
@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}


@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}


# Day 2 - Filter
@app.get("/products/filter")
def filter_products(
    category: str = Query(None, description="Electronics or Stationery"),
    min_price: int = Query(None, description="Minimum price"),
    max_price: int = Query(None, description="Maximum price"),
    in_stock: bool = Query(None, description="True = in stock only"),
):
    result = filter_products_logic(category, min_price, max_price, in_stock)
    return {"filtered_products": result, "count": len(result)}


# Day 3 - Compare
@app.get("/products/compare")
def compare_products(
    product_id_1: int = Query(..., description="First product ID"),
    product_id_2: int = Query(..., description="Second product ID"),
):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)

    if not p1:
        return {"error": f"Product {product_id_1} not found"}

    if not p2:
        return {"error": f"Product {product_id_2} not found"}

    cheaper = p1 if p1["price"] < p2["price"] else p2

    return {
        "product_1": p1,
        "product_2": p2,
        "better_value": cheaper["name"],
        "price_diff": abs(p1["price"] - p2["price"]),
    }

# product audit
@app.get("/products/audit")
def product_audit():

    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]

    stock_value = sum(p["price"] * 10 for p in in_stock_list)

    priciest = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": stock_value,
        "most_expensive": {
            "name": priciest["name"],
            "price": priciest["price"]
        }
    }

# product discount
@app.put("/products/discount")
def bulk_discount(
    category: str = Query(..., description="Category to discount"),
    discount_percent: int = Query(..., ge=1, le=99, description="Discount percent"),
):

    updated = []

    for p in products:
        if p["category"] == category:
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {"message": f"No products found in category: {category}"}

    return {
        "message": f"{discount_percent}% discount applied to {category}",
        "updated_count": len(updated),
        "updated_products": updated,
    }
#  Add Product
@app.post("/products")
def add_product(new_product: NewProduct, response: Response):
    existing_names = [p["name"].lower() for p in products]

    if new_product.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Product with this name already exists"}

    next_id = max(p["id"] for p in products) + 1

    product = {
        "id": next_id,
        "name": new_product.name,
        "price": new_product.price,
        "category": new_product.category,
        "in_stock": new_product.in_stock,
    }

    products.append(product)
    response.status_code = status.HTTP_201_CREATED

    return {"message": "Product added", "product": product}


#  Update Product
@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    response: Response,
    in_stock: bool = Query(None, description="Update stock status"),
    price: int = Query(None, description="Update price"),
):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if in_stock is not None:
        product["in_stock"] = in_stock

    if price is not None:
        product["price"] = price

    return {"message": "Product updated", "product": product}


#  Delete Product
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}
