from functools import wraps
from sqlalchemy import create_engine, text, Column, MetaData, String, Integer, Table, ForeignKey, inspect
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
from pathlib import Path
import requests
import traceback
import os


# you can only change this variable
YOUR_IP = "127.0.0.1"

def grader(f: callable):
    @wraps(f)
    def dec(*args, **kwargs):
        print("-" * 100)
        print(f.__name__)
        print("-" * 100)
        global MAX_SCORE, FINAL_SCORE
        MAX_SCORE, FINAL_SCORE = 0, 0
        try:
            f(*args, **kwargs)
        finally:
            res = FINAL_SCORE, MAX_SCORE
            # reset final score before returning
            FINAL_SCORE = 0
            return res

    return dec


# https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html
class COL:
    PASS = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    BLUE = "\033[94m"
    UNDERLINE = "\033[4m"


class Scorer:
    def __enter__(self):
        pass

    def __init__(self, score: int, desc: str):
        self.score = score
        global MAX_SCORE
        MAX_SCORE += score
        print(f"{COL.BOLD}{desc}{COL.ENDC} ({self.score} pts)")

    def __exit__(self, exc_type, exc_value, exc_tb):
        # add maximum score when passing these statements, otherwise 0
        if not exc_type:
            global FINAL_SCORE
            FINAL_SCORE += self.score
            print(COL.PASS, f"\tPASS: {self.score} pts", COL.ENDC)
        else:
            err_lines = [exc_type.__name__, *str(exc_value).split("\n")]
            errs = [
                "\t" + (" " * 4 if index else "") + line
                for index, line in enumerate(err_lines)
            ]
            print("{}{}".format(COL.WARNING, "\n".join(errs)))
            print(f"\t{COL.FAIL}FAIL: 0 pts", COL.ENDC)

        # skip throwing the exception
        return True


def assert_eq(
    expression, expected, exc_type=AssertionError, hide: bool = False, err_msg=None
):
    try:
        if expression == expected:
            return
        else:
            errs = [err_msg] if err_msg else []
            if hide:
                expected = "<hidden>"
            err = "\n".join(
                [*errs, f"> Expected: {expected}", f"> Yours: {expression}"]
            )
            raise exc_type(err)
    except Exception:
        raise


class safe_init:
    def __enter__(self):
        pass

    def __init__(self, max_score: int):
        self.max_score = max_score

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type:
            print(traceback.format_exc())
            global MAX_SCORE
            MAX_SCORE = self.max_score
            return False

        return True

class IsString:
    def __eq__(self, other):
        return isinstance(other, str)

    def __repr__(self):
        return "<must_be_a_string>"


def assert_include(
    expression, expected, exc_type=AssertionError, hide: bool = False, err_msg=None
):
    try:
        if expected in expression:
            return
        else:
            errs = [err_msg] if err_msg else []
            if hide:
                expected = "<hidden>"
            err = "\n".join([*errs, f"> there is no {expected} in  {expression}"])
            raise exc_type(err)
    except Exception:
        raise


def assert_response(
    method: str,
    endpoint: str,
    json: dict = None,
    exp_json=None,
    exp_code: int = None,
    headers: dict = None,
):
    response = method(endpoint, json=json, headers=headers)
    # print(response.json())
    assert_eq(response.json(), exp_json)
    assert_eq(response.status_code, exp_code)


def assert_response_include(
    method: str,
    endpoint: str,
    exp_json=None,
    exp_code: int = None,
):
    response = method(endpoint)
    # print(response.json())
    assert_include(response.json(), exp_json)
    assert_eq(response.status_code, exp_code)


HOST = f"http://{YOUR_IP}:5000"

load_dotenv(".env")

def get_engine():
    """Creating SQLite Engine to interact"""

    engine_uri = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PASSWORD"),
        os.getenv("POSTGRES_HOST"),
        os.getenv("POSTGRES_PORT"),
        os.getenv("POSTGRES_DB"),
    )

    return create_engine(engine_uri, future=True)


def get_response( method: str, endpoint: str, json: dict = None,):
    """
    Get Response from API CALL

    Will be useful to get UUID after call create endpoint since uuid is random and not a part of create endpoint response
    UUID will be used to call update, delete, etc
    """
    response = method(endpoint, json=json)
    # print(response.json())
    return response.json()

@grader
def ingredients_endpoint():
    # with safe_init(5):
    #     pass

    with Scorer(1, "1 [ Create Ingredient ] Invalid Input"):
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "nama" : "nasi"
            },
            exp_json={"error" : "the name field is required"},
            exp_code=400,
        )
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "name" : 44
            },
            exp_json={"error" : "the name must be a string"},
            exp_code=400,
        )
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "name" : "a"
            },
            exp_json={"error" : "the name must be beetween 2 and 64 characters"},
            exp_code=400,
        )
    with Scorer(1, "1 [ Create Ingredient ] Success - Create 7 Ingredients"):
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "name" : "nasi"
            },
            exp_json={"message": "ingredient nasi added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "name" : "telur"
            },
            exp_json={"message": "ingredient telur added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "name" : "minyak"
            },
            exp_json={"message": "ingredient minyak added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "name" : "garam"
            },
            exp_json={"message": "ingredient garam added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "name" : "es"
            },
            exp_json={"message": "ingredient es added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "name" : "gula"
            },
            exp_json={"message": "ingredient gula added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "name" : "teh"
            },
            exp_json={"message": "ingredient teh added successfully"},
            exp_code=201,
        )
    with Scorer(1, "1 [ Create Ingredient ] Failed - Ingredient Already Exist"):
        assert_response(
            requests.post,
            f"{HOST}/ingredients",
            json={
                "name" : "NASI"
            },
            exp_json={"error": "ingredient with the same name already exists"},
            exp_code=400,
        )
    
    with Scorer(1, "2 [ Get All Ingredients ] Show all ingredient"):
        assert_response(
            requests.get,
            f"{HOST}/ingredients",
            exp_json={
                "data": [
                    {
                        "id": 1,
                        "name": "nasi"
                    },
                    {
                        "id": 2,
                        "name": "telur"
                    },
                    {
                        "id": 3,
                        "name": "minyak"
                    },
                    {
                        "id": 4,
                        "name": "garam"
                    },
                    {
                        "id": 5,
                        "name": "es"
                    },
                    {
                        "id": 6,
                        "name": "gula"
                    },
                    {
                        "id": 7,
                        "name": "teh"
                    },

                ],
                "message": "Success",
                "total_rows": 7
            },
            exp_code=200,
        )
    
    with Scorer(1, "3 [ Get An Ingredient ] Invalid ID / not found"):
        assert_response(
            requests.get,
            f"{HOST}/ingredients/10",
            exp_json={"error" : "ingredient not found"},
            exp_code=404,
        )
    with Scorer(1, "3 [ Get An Ingredient ] Valid ID / success"):
        assert_response(
            requests.get,
            f"{HOST}/ingredients/5",
            exp_json={
                "data": [
                    {
                        "id": 5,
                        "name": "es"
                    }
                ],
                "message": "Success"
            },
            exp_code=200,
        )
    
    with Scorer(1, "4 [ Update Ingredients ] Invalid Input"):
        assert_response(
            requests.put,
            f"{HOST}/ingredients/1",
            json={
                "nama" : "nasi"
            },
            exp_json={"error" : "the name field is required"},
            exp_code=400,
        )
        assert_response(
            requests.put,
            f"{HOST}/ingredients/1",
            json={
                "name" : 123
            },
            exp_json={"error" : f"the name must be a string"},
            exp_code=400,
        )
        assert_response(
            requests.put,
            f"{HOST}/ingredients/1",
            json={
                "name" : "a"
            },
            exp_json={"error" : f"the name must be beetween 2 and 64 characters"},
            exp_code=400,
        )
        assert_response(
            requests.put,
            f"{HOST}/ingredients/12",
            json={
                "name" : "nasi"
            },
            exp_json={"error": f"ingredient not found"},
            exp_code=404,
        )
    with Scorer(1, "4 [ Update Ingredients ] Success"):
        assert_response(
            requests.put,
            f"{HOST}/ingredients/1",
            json={
                "name" : "nasi putih"
            },
            exp_json={"message" : "ingredient updated successfully"},
            exp_code=200,
        )
    with Scorer(1, "4 [ Update Ingredients ] Failed - Ingredient Already Exist"):
        assert_response(
            requests.put,
            f"{HOST}/ingredients/1",
            json={
                "name" : "ES"
            },
            exp_json={"error": f"ingredient with the same name already exists"},
            exp_code=400,
        )
    
    with Scorer(1, "5 [ Delete Ingredients ] Invalid ID / Ingredient Not Found"):
        assert_response(
            requests.delete,
            f"{HOST}/ingredients/12",
            exp_json={"error" : f"ingredient not found"},
            exp_code=404,
        )
    with Scorer(1, "5 [ Delete Ingredients ] Success"):
        assert_response(
            requests.delete,
            f"{HOST}/ingredients/4",
            exp_json={"message": f"ingredient deleted successfully"},
            exp_code=200,
        )

@grader
def categories_endpoint():
    # with safe_init(5):
    #     pass
    
    with Scorer(1, "1 [ Create Category ] Invalid Input"):
        assert_response(
            requests.post,
            f"{HOST}/categories",
            json={
                "nama" : "nasi"
            },
            exp_json={"error" : "the name field is required"},
            exp_code=400,
        )
        assert_response(
            requests.post,
            f"{HOST}/categories",
            json={
                "name" : 123
            },
            exp_json={"error" : f"the name must be a string"},
            exp_code=400,
        )
        assert_response(
            requests.post,
            f"{HOST}/categories",
            json={
                "name" : "a"
            },
            exp_json={"error" : f"the name must be beetween 2 and 64 characters"},
            exp_code=400,
        )
    with Scorer(1, "1 [ Create Category ] Success - Create 3 Categories"):
        assert_response(
            requests.post,
            f"{HOST}/categories",
            json={
                "name" : "makanan"
            },
            exp_json={"message": f"category makanan added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/categories",
            json={
                "name" : "minuman"
            },
            exp_json={"message": f"category minuman added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/categories",
            json={
                "name" : "snack"
            },
            exp_json={"message": f"category snack added successfully"},
            exp_code=201,
        )
    with Scorer(1, "1 [ Create Category ] Failed - Category Already Exist"):
        assert_response(
            requests.post,
            f"{HOST}/categories",
            json={
                "name" : "Minuman"
            },
            exp_json={"error": "category with the same name already exists"},
            exp_code=400,
        )

    with Scorer(1, "2 [ Get All Categories ] Show all categories"):
        assert_response(
            requests.get,
            f"{HOST}/categories",
            exp_json={
                "data": [
                    {
                        "id": 1,
                        "name": "makanan"
                    },
                    {
                        "id": 2,
                        "name": "minuman"
                    },
                    {
                        "id": 3,
                        "name": "snack"
                    }
                ],
                "message": "Success",
                "total_rows": 3
            },
            exp_code=200,
        )

    with Scorer(1, "3 [ Get A Category ] Invalid ID / not found"):
        assert_response(
            requests.get,
            f"{HOST}/categories/4",
            exp_json={"error" : f"category not found"},
            exp_code=404,
        )
    with Scorer(1, "3 [ Get A Category ] Valid ID / Success"):
        assert_response(
            requests.get,
            f"{HOST}/categories/3",
            exp_json={
                "data": [
                    {
                        "id": 3,
                        "name": "snack"
                    }
                ],
                "message": "Success"
            },
            exp_code=200,
        )

    with Scorer(1, "4 [ Update Category ] Invalid Input"):
        assert_response(
            requests.put,
            f"{HOST}/categories/3",
            json={
                "nama" : "nasi"
            },
            exp_json={"error" : "the name field is required"},
            exp_code=400,
        )
        assert_response(
            requests.put,
            f"{HOST}/categories/3",
            json={
                "name" : 123
            },
            exp_json={"error" : f"the name must be a string"},
            exp_code=400,
        )
        assert_response(
            requests.put,
            f"{HOST}/categories/3",
            json={
                "name" : "a"
            },
            exp_json={"error" : f"the name must be beetween 2 and 64 characters"},
            exp_code=400,
        )
    with Scorer(1, "4 [ Update Category ] Success"):
        assert_response(
            requests.put,
            f"{HOST}/categories/3",
            json={
                "name" : "makanan ringan"
            },
            exp_json={"message": f"category updated successfully"},
            exp_code=200,
        )

    with Scorer(1, "5 [ Delete Category ] Invalid ID / Ingredient Not Found"):
        assert_response(
            requests.delete,
            f"{HOST}/categories/4",
            exp_json={"error" : f"category not found"},
            exp_code=404,
        )
    with Scorer(1, "5 [ Delete Category ] Valid ID / Success"):
        assert_response(
            requests.delete,
            f"{HOST}/categories/3",
            exp_json={"message": f"category deleted successfully"},
            exp_code=200,
        )

@grader
def recipes_endpoint():
    # with safe_init(5):
    #     pass
    
    with Scorer(1, "1 [ Create Recipes ] Invalid Name"):
        assert_response(
            requests.post,
            f"{HOST}/recipes",
            json={
                "name" : "n",
                "category_id" : 1,
                "ingredients" : [
                    {
                        "id" : 1,
                        "quantity" : "1 piring"
                    },
                    {
                        "id" : 2,
                        "quantity" : "2 butir"
                    },
                    {
                        "id" : 3,
                        "quantity" : "secukupnya"
                    }
                ]
            },
            exp_json={"error" : f"the name must be beetween 2 and 64 characters"},
            exp_code=400,
        )
    with Scorer(1, "1 [ Create Recipes ] Invalid Category"):
        assert_response(
            requests.post,
            f"{HOST}/recipes",
            json={
                "name" : "nasi telur",
                "category_id" : 5,
                "ingredients" : [
                    {
                        "id" : 1,
                        "quantity" : "1 piring"
                    },
                    {
                        "id" : 2,
                        "quantity" : "2 butir"
                    },
                    {
                        "id" : 3,
                        "quantity" : "secukupnya"
                    }
                ]
            },
            exp_json={"error": "invalid category ID"},
            exp_code=400,
        )
    with Scorer(1, "1 [ Create Recipes ] Invalid Ingredients"):
        assert_response(
            requests.post,
            f"{HOST}/recipes",
            json={
                "name" : "nasi telur",
                "category_id" : 1,
                "ingredients" : [
                    {
                        "id" : 1,
                        "quantity" : "1 piring"
                    },
                    {
                        "id" : 2,
                        "quantity" : "2 butir"
                    },
                    {
                        "id" : 50,
                        "quantity" : "secukupnya"
                    }
                ]
            },
            exp_json={"error": "invalid ingredient ID"},
            exp_code=400,
        )
    with Scorer(1, "1 [ Create Recipes ] Success - Create 3 Recipes"):
        assert_response(
            requests.post,
            f"{HOST}/recipes",
            json={
                "name" : "nasi telur",
                "category_id" : 1,
                "ingredients" : [
                    {
                        "id" : 1,
                        "quantity" : "1 piring"
                    },
                    {
                        "id" : 2,
                        "quantity" : "2 butir"
                    },
                    {
                        "id" : 3,
                        "quantity" : "secukupnya"
                    }
                ]
            },
            exp_json={"message": f"recipe nasi telur added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/recipes",
            json={
                "name" : "es teh",
                "category_id" : 2,
                "ingredients" : [
                    {
                        "id" : 5,
                        "quantity" : "3 buah"
                    },
                    {
                        "id" : 7,
                        "quantity" : "1 gelas"
                    },
                ]
            },
            exp_json={"message": f"recipe es teh added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/recipes",
            json={
                "name" : "es teh tawar",
                "category_id" : 2,
                "ingredients" : [
                    {
                        "id" : 5,
                        "quantity" : "3 buah"
                    },
                    {
                        "id" : 7,
                        "quantity" : "1 gelas"
                    },
                ]
            },
            exp_json={"message": f"recipe es teh tawar added successfully"},
            exp_code=201,
        )
        assert_response(
            requests.post,
            f"{HOST}/recipes",
            json={
                "name" : "telur dadar",
                "category_id" : 1,
                "ingredients" : [
                    {
                        "id" : 2,
                        "quantity" : "1 butir"
                    },
                    {
                        "id" : 3,
                        "quantity" : "secukupnya"
                    },
                ]
            },
            exp_json={"message": f"recipe telur dadar added successfully"},
            exp_code=201,
        )

    with Scorer(1, "2 [ Get Recipe ] Success"):
         assert_response(
            requests.get,
            f"{HOST}/recipes/1",
            exp_json={
                "data": {
                    "category_id": 1,
                    "category_name": "makanan",
                    "id": 1,
                    "ingredients": [                        
                        {
                            "ing_id": 2,
                            "ing_name": "telur",
                            "quantity": "2 butir"
                        },
                        {
                            "ing_id": 3,
                            "ing_name": "minyak",
                            "quantity": "secukupnya"
                        },
                        {
                            "ing_id": 1,
                            "ing_name": "nasi putih",
                            "quantity": "1 piring"
                        }
                    ],
                    "name": "nasi telur"
                },
                "message": "Success"
            },
            exp_code=200,
        )

    with Scorer(1, "3 [ Update Recipe ] Success"):
        assert_response(
            requests.put,
            f"{HOST}/recipes/2",
            json={
                "name" : "es teh manis",
                "category_id" : 2,
                "ingredients" : [
                    {
                        "id" : 5,
                        "quantity" : "3 buah"
                    },
                    {
                        "id" : 6,
                        "quantity" : "1 sendok"
                    },
                    {
                        "id" : 7,
                        "quantity" : "1 gelas"
                    },
                ]
            },
            exp_json={"message": f"recipe es teh manis updated successfully"},
            exp_code=200,
        )

    with Scorer(1, "4 [ Delete Recipe ] Success"):
        assert_response(
            requests.delete,
            f"{HOST}/recipes/4",
            exp_json={"message": f"recipe deleted successfully"},
            exp_code=200,
        )

@grader
def recipes_list():
    with Scorer(1, "4 [ Recipe List ] No Filter Success"):
        assert_response(
            requests.get,
            f"{HOST}/recipes",
            exp_json={
                "data": [
                    {
                        "category_id": 1,
                        "category_name": "makanan",
                        "id": 1,
                        "ingredients" : [                            
                            {
                                "ing_id" : 2,
                                "ing_name": "telur",
                                "quantity" : "2 butir"
                            },
                            {
                                "ing_id" : 3,
                                "ing_name": "minyak",
                                "quantity" : "secukupnya"
                            },
                            {
                                "ing_id" : 1,
                                "ing_name": "nasi putih",
                                "quantity" : "1 piring"
                            }
                        ],
                        "name": "nasi telur"
                    },
                    {
                        "category_id": 2,
                        "category_name": "minuman",
                        "id": 3,
                        "ingredients" : [
                            {
                                "ing_id" : 5,
                                "ing_name": "es",
                                "quantity" : "3 buah"
                            },
                            {
                                "ing_id" : 7,
                                "ing_name": "teh",
                                "quantity" : "1 gelas"
                            }
                        ],
                        "name": "es teh tawar"
                    },
                    {
                        "category_id": 2,
                        "category_name": "minuman",
                        "id": 2,
                        "ingredients" : [
                            {
                                "ing_id" : 5,
                                "ing_name": "es",
                                "quantity" : "3 buah"
                            },
                            {
                                "ing_id" : 6,
                                "ing_name": "gula",
                                "quantity" : "1 sendok"
                            },
                            {
                                "ing_id" : 7,
                                "ing_name": "teh",
                                "quantity" : "1 gelas"
                            }
                        ],
                        "name": "es teh manis"
                    }                    
                ],
                "message": "Success",
                "total_rows": 3
            },
            exp_code=200,
        )
    with Scorer(1, "4 [ Recipe List ] Use Filter Success"):
        assert_response(
            requests.get,
            f"{HOST}/recipes?ingredients_id=6&category_id=2",
            exp_json={
                "data": [
                    {
                        "category_id": 2,
                        "category_name": "minuman",
                        "id": 2,
                        "ingredients" : [
                            {
                                "ing_id" : 5,
                                "ing_name": "es",
                                "quantity" : "3 buah"
                            },
                            {
                                "ing_id" : 6,
                                "ing_name": "gula",
                                "quantity" : "1 sendok"
                            },
                            {
                                "ing_id" : 7,
                                "ing_name": "teh",
                                "quantity" : "1 gelas"
                            }
                        ],
                        "name": "es teh manis"
                    },
                ],
                "message": "Success",
                "total_rows": 1
            },
            exp_code=200,
        )


def highlight(s: str):
    print("=" * 100 + "\n")
    print(s)
    print("\n" + "=" * 100)


if __name__ == "__main__":
    
    # drop all table
    engine = get_engine()
    meta = MetaData()

    # recreate table
    Table(
            "ingredients",
            meta,
            Column("id", Integer, primary_key=True),
            Column("name", String, unique=True, nullable=False),
        )
    Table(
            "categories",
            meta,
            Column("id", Integer, primary_key=True),
            Column("name", String, unique=True, nullable=False),
        )
    Table(
            "recipes",
            meta,
            Column("id", Integer, primary_key=True),
            Column("name", String, unique=True, nullable=False),
            Column("category_id", Integer, ForeignKey("categories.id")),
        )
    Table(
            "recipes_ingredients",
            meta,
            Column("id", Integer, primary_key=True),
            Column("recipe_id", Integer, ForeignKey("recipes.id")),
            Column("ingredient_id", Integer, ForeignKey("ingredients.id")),
            Column("quantity", String, nullable=False),
        )
    
    meta.drop_all(engine)
    meta.create_all(engine)
    
    # from app.app import app

    highlight("Testing Recipe Book API...")
    tests = [ingredients_endpoint, categories_endpoint, recipes_endpoint, recipes_list]

    # app.config.update({"TESTING": True})
    # c = app.test_client()

    final_score = 0
    perfect_score = 0
    for test_f in tests:
        total_score, total_weight = test_f()
        final_score += total_score
        perfect_score += total_weight

    highlight(
        f"{COL.BOLD}TESTING SCORE:{COL.ENDC} "
        + f"{COL.BLUE}{final_score}/{perfect_score}"
    )
