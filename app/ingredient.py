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

ingredient_bp = Blueprint("ingredients_blueprint", __name__, url_prefix="/ingredients")

@ingredient_bp.route("", methods=["POST"])
def add_ingredient():
    # Get JSON data
    data = request.json

    # Data checking and validation
    if "name" not in data :
        return {"error" : "the name field is required"}, 400
    if not isinstance(data["name"], str) :
        return {"error" : "the name must be a string"}, 400
    if not (2 <= len(data["name"]) <= 64) :
        return {"error" : "the name must be beetween 2 and 64 characters"}, 400
    
    # Check ingredient is exist
    data_name = data['name'].lower()
    ingredients = run_query(f''' SELECT * FROM ingredients WHERE name='{data_name}' ''')
    if len(ingredients) != 0 :
        return{"error": "ingredient with the same name already exists"}, 400

    # Insert to database
    run_query(f''' INSERT INTO ingredients (name) VALUES ('{data_name}') ''', True)
    return {"message": f"ingredient {data_name} added successfully"}, 201


@ingredient_bp.route("", methods=["GET"])
def get_all_ingredient():
    ingredients = run_query(f"SELECT * FROM ingredients")
    return {
        "message": "Success",
        "data": ingredients,
        "total_rows": len(ingredients)
    }, 200


@ingredient_bp.route("/<int:id>", methods=["GET"])
def get_ingredient(id):
    if not isinstance(id, int) :
        return {"error" : "the id must be an integer"}, 400

    ingredients = run_query(f''' SELECT * FROM ingredients WHERE id='{id}' ''')
    if len(ingredients)==0 :
        return {"error" : "ingredient not found"}, 404
    else :
        return {
            "message": "Success",
            "data": ingredients,
        }, 200


@ingredient_bp.route("/<int:id>", methods=["PUT"])
def update_ingredient(id):
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
    
    # Check ingredient with the id is exist and the name has not taken
    data_name = data['name'].lower()
    ingredients = run_query('SELECT * FROM ingredients')

    if not any(ingredient["id"] == id for ingredient in ingredients) :
        return {"error": f"ingredient not found"}, 404
    if any(ingredient["name"].lower() == data_name for ingredient in ingredients) :
        return {"error": f"ingredient with the same name already exists"}, 400

    # Update to database    
    run_query(f''' UPDATE ingredients SET name = '{data_name}' WHERE id='{id}' ''', True)
    return {"message": f"ingredient updated successfully"}, 200


@ingredient_bp.route("/<int:id>", methods=["DELETE"])
def delete_ingredient(id):
    if not isinstance(id, int) :
        return {"error" : f"the id must be an integer"}, 400
    
    ingredients = run_query(f''' SELECT * FROM ingredients WHERE id='{id}' ''')
    if len(ingredients)==0 :
        return {"error" : f"ingredient not found"}, 404
    
    ingredients = run_query(f''' SELECT * FROM recipes_ingredients WHERE ingredient_id='{id}' ''')
    if len(ingredients)!=0 :
        return {"error" : f"ingredient is being used by a recipe"}, 400

    run_query(f''' DELETE FROM ingredients WHERE id='{id}' ''', True)
    return {"message": f"ingredient deleted successfully"}, 200
