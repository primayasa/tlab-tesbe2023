from sqlalchemy import Column, MetaData, String, Integer, Table, ForeignKey, inspect
from sqlalchemy.exc import IntegrityError
from utils import get_engine
from flask import Flask

from ingredient import ingredient_bp
from category import category_bp
from recipe import recipe_bp

def create_app():
    app = Flask(__name__)

    engine = get_engine()
    meta = MetaData()

    if not inspect(engine).has_table("ingredients"):
        Table(
            "ingredients",
            meta,
            Column("id", Integer, primary_key=True),
            Column("name", String, unique=True, nullable=False),
        )

    if not inspect(engine).has_table("categories"):
        Table(
            "categories",
            meta,
            Column("id", Integer, primary_key=True),
            Column("name", String, unique=True, nullable=False),
        )

    if not inspect(engine).has_table("recipes"):
        Table(
            "recipes",
            meta,
            Column("id", Integer, primary_key=True),
            Column("name", String, unique=True, nullable=False),
            Column("category_id", Integer, ForeignKey("categories.id")),
        )

    if not inspect(engine).has_table("recipes_ingredients"):
        Table(
            "recipes_ingredients",
            meta,
            Column("id", Integer, primary_key=True),
            Column("recipe_id", Integer, ForeignKey("recipes.id")),
            Column("ingredient_id", Integer, ForeignKey("ingredients.id")),
            Column("quantity", String, nullable=False),
        )

    meta.create_all(engine)

    blueprints = [ingredient_bp, category_bp, recipe_bp]
    for bp in blueprints:
        app.register_blueprint(bp)

    return app

app = create_app()

# FOR TESTING PURPOSE ONLY
# TO CHECK IF THE APP RUN WELL
@app.route('/')
def index():
    return {'message': 'Hello from Flask!'}, 200

if __name__ == "__main__":
    app.run(debug=True)