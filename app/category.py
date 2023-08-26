from utils import get_engine, run_query
from flask import Blueprint, request
from sqlalchemy import (
    MetaData,
    Table,
    delete,
    insert,
    select,
)
from sqlalchemy.exc import IntegrityError


category_bp = Blueprint("categories_blueprint", __name__, url_prefix="/categories")


@category_bp.route("", methods=["POST"])
def add_category():
    # Get JSON data
    data = request.json

    # Data checking and validation
    if "name" not in data :
        return {"error" : f"the name field is required"}, 400
    if not isinstance(data["name"], str) :
        return {"error" : f"the name must be a string"}, 400
    if not (2 <= len(data["name"]) <= 64) :
        return {"error" : f"the name must be beetween 2 and 64 characters"}, 400
    
    # Check category with the title is exist
    data_name = data['name'].lower()
    categories = run_query(f''' SELECT * FROM categories WHERE name='{data_name}' ''')
    if len(categories) != 0 :
        return{"error": "category with the same name already exists"}, 400

    # Insert to database
    run_query(f''' INSERT INTO categories (name) VALUES ('{data_name}') ''', True)
    return {"message": f"category {data_name} added successfully"}, 201


@category_bp.route("", methods=["GET"])
def get_all_category():
    categories = run_query(f"SELECT * FROM categories")
    return {
        "message": "Success",
        "data": categories,
        "total_rows": len(categories)
    }, 200


@category_bp.route("/<int:id>", methods=["GET"])
def get_category(id):
    if not isinstance(id, int) :
        return {"error" : "the id must be an integer"}, 400

    categories = run_query(f''' SELECT * FROM categories WHERE id='{id}' ''')
    if len(categories)==0 :
        return {"error" : f"category not found"}, 404
    else :
        return {
            "message": "Success",
            "data": categories,
        }, 200


@category_bp.route("/<int:id>", methods=["PUT"])
def update_category(id):
    # Get JSON data
    data = request.json

    # Data checking and validation
    if not isinstance(id, int) :
        return {"error" : f"the id must be an integer"}, 400

    if "name" not in data :
        return {"error" : f"the name field is required"}, 400
    if not isinstance(data["name"], str) :
        return {"error" : f"the name must be a string"}, 400    
    if not (2 <= len(data["name"]) <= 64) :
        return {"error" : f"the name must be beetween 2 and 64 characters"}, 400
    
    # Check category with the id is exist and the name has not taken
    data_name = data['name'].lower()
    categories = run_query('SELECT * FROM categories')
    if not any(category["id"] == id for category in categories) :
        return {"error": f"category not found"}, 404
    if any(category["name"].lower() == data_name for category in categories) :
        return {"error": f"category with the same name already exists"}, 400

    # Update to database
    run_query(f''' UPDATE categories SET name = '{data_name}' WHERE id='{id}' ''', True)
    return {"message": f"category updated successfully"}, 200


@category_bp.route("/<int:id>", methods=["DELETE"])
def delete_category(id):
    if not isinstance(id, int) :
        return {"error" : f"the id must be an integer"}, 400
    
    categories = run_query(f''' SELECT * FROM categories WHERE id='{id}' ''')
    if len(categories)==0 :
        return {"error" : f"category not found"}, 404
   
    categories = run_query(f''' SELECT * FROM recipes WHERE category_id='{id}' ''')
    if len(categories)!=0 :
        return {"error" : f"category is being used by a recipe"}, 400
    
    run_query(f''' DELETE FROM categories WHERE id='{id}' ''', True)
    return {"message": f"category deleted successfully"}, 200