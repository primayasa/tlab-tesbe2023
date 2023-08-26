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
import re


recipe_bp = Blueprint("recipes_blueprint", __name__, url_prefix="/recipes")


@recipe_bp.route("", methods=["POST"])
def add_recipe():
    data = request.json

    # validate name
    if "name" not in data :
        return {"error" : f"the name field is required"}, 400
    if not isinstance(data["name"], str) :
        return {"error" : f"the name must be a string"}, 400
    if not (2 <= len(data["name"]) <= 64) :
        return {"error" : f"the name must be beetween 2 and 64 characters"}, 400  
      
    data_name = data['name'].lower()
    recipes = run_query(f''' SELECT * FROM recipes WHERE name='{data_name}' ''')
    if len(recipes) != 0 :
        return{"error": "recipe with the same name already exists"}, 400

    # validate category
    if "category_id" not in data :
        return {"error" : f"the category_id field is required"}, 400
    if not isinstance(data["category_id"], int) :
        return {"error" : f"the category_id must be an integer"}, 400
    
    category = run_query(f''' SELECT * FROM categories WHERE id='{data["category_id"]}' ''')
    if len(category) == 0 :
        return{"error": "invalid category ID"}, 400

    # validate ingredients
    if "ingredients" not in data :
        return {"error" : f"the ingredients field is required"}, 400
        
    ingredients_data = data['ingredients']
    ingredients_db = run_query(f''' SELECT id FROM ingredients ''')

    for ingredient in ingredients_data :
        if "id" not in ingredient :
            return {"error" : f"the ingredients id is required"}, 400        
        if not any(item["id"] == ingredient["id"] for item in ingredients_db):
            return {"error": "invalid ingredient ID"}, 400
            
        if "quantity" not in ingredient :
            return {"error" : f"the quantity id is required"}, 400
        if not isinstance(ingredient["quantity"], str) :
            return {"error" : f"the quantity must be a string"}, 400
        if not (2 <= len(ingredient["quantity"]) <= 64):
            return {"error": "the quantity must be beetween 2 and 64 characters"}, 400

    # Insert to database
    run_query(f''' INSERT INTO recipes (name, category_id) VALUES ('{data_name}', '{data["category_id"]}') ''', True)
    recipe = run_query(f''' SELECT id FROM recipes WHERE name='{data_name}' ''')[0]
    
    for ingredient in ingredients_data :
        run_query(f''' INSERT INTO recipes_ingredients (recipe_id, ingredient_id, quantity) 
                       VALUES ('{recipe['id']}', '{ingredient['id']}', '{ingredient['quantity']}') 
                   ''', True)

    return {"message": f"recipe {data_name} added successfully"}, 201


@recipe_bp.route("", methods=["GET"])
def get_all_recipe():
    data = request.args

    query = f'''
            SELECT
                r.id as id, r.name as name, c.id as cat_id, c.name as cat_name		
            FROM recipes r
            JOIN categories c
                ON r.category_id = c.id
            JOIN recipes_ingredients ri
                ON r.id = ri.recipe_id		
            WHERE 1=1
            '''

    # filter category
    if "category_id" in data :       
        if not isinstance(data["category_id"], str) :
            return {"error" : f"the category_id must be an string"}, 400
        if not data["category_id"].isdigit() :
             return {"error" : f"the category_id must be numeric"}, 400
    
        category = run_query(f''' SELECT * FROM categories WHERE id='{data["category_id"]}' ''')
        if len(category) == 0 :
            return{"error": "invalid category ID"}, 400
        
        query += f" AND c.id = '{data['category_id']}'"

    
    # filter ingredient
    if "ingredients_id" in data :       
        if not isinstance(data["ingredients_id"], str) :
            return {"error" : f"the ingredients must be string"}, 400
        
        pattern = r'^\d+(,\d+)*$'
        if not re.match(pattern, data["ingredients_id"]) :
            return {"error" : f"the ingredients should be numeric and separated by comma"}, 400
        
        data_ingredients = [int(num) for num in data["ingredients_id"].split(',')]
        ingredients_filter = f" AND ri.ingredient_id IN ("
        for index, ing in enumerate(data_ingredients):
            if index != len(data_ingredients) - 1:
                ingredients_filter += f"'{ing}',"
            else:
                ingredients_filter += f"'{ing}'"
        ingredients_filter += ")"

        query += ingredients_filter
    
    query += " GROUP BY r.id, c.id;"
    recipes = run_query(query)
    if len(recipes)==0 :
        return {
        "message": "Success",
            "data": recipes,
            "total_rows": len(recipes)
        }, 200
    
    recipes_response = []
    for recipe in recipes :
        query = f'''
                    SELECT i.id as ing_id, i.name as ing_name, ri.quantity as quantity
                    FROM recipes_ingredients ri
                    JOIN ingredients i
                        ON ri.ingredient_id = i.id
                    WHERE ri.recipe_id = '{recipe['id']}'
                '''
        ingredients = run_query(query)
        
        recipe_response = {
            "id"   : recipe['id'],
            "name" : recipe['name'],
            "category_id" : recipe['cat_id'],
            "category_name" : recipe['cat_name'],
            "ingredients" : ingredients
        }

        recipes_response.append(recipe_response)

    return {
        "message": "Success",
        "data": recipes_response,
        "total_rows": len(recipes_response)
    }, 200


@recipe_bp.route("/<int:id>", methods=["GET"])
def get_recipe(id):
    if not isinstance(id, int) :
        return {"error" : "the id must be an integer"}, 400
    
    # Check recipe ID
    recipes = run_query( f'''
                            SELECT
                                r.id as id, r.name as name, c.id as cat_id, c.name as cat_name		
                            FROM recipes r
                            JOIN categories c
                                ON r.category_id = c.id
                            WHERE r.id = {id};
                        ''')
    if len(recipes)==0 :
        return {"error" : f"recipe not found"}, 404
    
    # Get Ingrediets
    recipe = recipes[0]
    query = f'''
                SELECT i.id as ing_id, i.name as ing_name, ri.quantity as quantity
                FROM recipes_ingredients ri
                JOIN ingredients i
                    ON ri.ingredient_id = i.id
                WHERE ri.recipe_id = '{recipe['id']}'
            '''
    ingredients = run_query(query)
    
    # return recipe
    recipe_response = {
        "id"   : recipe['id'],
        "name" : recipe['name'],
        "category_id" : recipe['cat_id'],
        "category_name" : recipe['cat_name'],
        "ingredients" : ingredients
    }

    return {
        "message": "Success",
        "data": recipe_response,
    }, 200


@recipe_bp.route("/<int:id>", methods=["PUT"])
def update_recipe(id):
    data = request.json

    # validate id
    if not isinstance(id, int) :
        return {"error" : "the id must be an integer"}, 400
    recipes = run_query(f''' SELECT * FROM recipes WHERE id='{id}' ''')
    if len(recipes) == 0 :
        return{"error": "invalid recipe ID"}, 400

    # validate name
    if "name" not in data :
        return {"error" : f"the name field is required"}, 400
    if not isinstance(data["name"], str) :
        return {"error" : f"the name must be a string"}, 400
    if not (2 <= len(data["name"]) <= 64) :
        return {"error" : f"the name must be beetween 2 and 64 characters"}, 400  
      
    data_name = data['name'].lower()
    recipes = run_query(f''' SELECT * FROM recipes WHERE name='{data_name}' AND id<>{id} ''')
    if len(recipes) != 0 :
        return{"error": "recipe with the same name already exists"}, 400

    # validate category
    if "category_id" not in data :
        return {"error" : f"the category_id field is required"}, 400
    if not isinstance(data["category_id"], int) :
        return {"error" : f"the category_id must be an integer"}, 400
    
    category = run_query(f''' SELECT * FROM categories WHERE id='{data["category_id"]}' ''')
    if len(category) == 0 :
        return{"error": "invalid category ID"}, 400

    # validate ingredients
    if "ingredients" not in data :
        return {"error" : f"the ingredients field is required"}, 400
        
    ingredients_data = data['ingredients']
    ingredients_db = run_query(f''' SELECT id FROM ingredients ''')

    for ingredient in ingredients_data :
        if "id" not in ingredient :
            return {"error" : f"the ingredients id is required"}, 400        
        if not any(item["id"] == ingredient["id"] for item in ingredients_db):
            return {"error": "invalid ingredient ID"}, 400
            
        if "quantity" not in ingredient :
            return {"error" : f"the quantity id is required"}, 400
        if not isinstance(ingredient["quantity"], str) :
            return {"error" : f"the quantity must be a string"}, 400
        if not (2 <= len(ingredient["quantity"]) <= 64):
            return {"error": "the quantity must be beetween 2 and 64 characters"}, 400

    # Update to Database
    run_query(f''' UPDATE recipes SET name='{data_name}', category_id={data["category_id"]} WHERE id = '{id}';''', True)
    run_query(f''' DELETE FROM recipes_ingredients WHERE recipe_id = {id}; ''', True)
    for ingredient in ingredients_data :
        run_query(f''' INSERT INTO recipes_ingredients (recipe_id, ingredient_id, quantity) 
                       VALUES ('{id}', '{ingredient['id']}', '{ingredient['quantity']}')
                   ''', True)

    return {"message": f"recipe {data_name} updated successfully"}, 200


@recipe_bp.route("/<int:id>", methods=["DELETE"])
def delete_recipe(id):
    # validate id
    if not isinstance(id, int) :
        return {"error" : "the id must be an integer"}, 400
    recipes = run_query(f''' SELECT * FROM recipes WHERE id='{id}' ''')
    if len(recipes) == 0 :
        return{"error": "invalid recipe ID"}, 400
    
    run_query(f''' DELETE FROM recipes_ingredients WHERE recipe_id = {id}; ''', True)
    run_query(f''' DELETE FROM recipes WHERE id = {id}; ''', True)

    return {"message": f"recipe deleted successfully"}, 200