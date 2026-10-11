"""
Lab 7, Part 2: a REST API for your houseplants
==============================================

Do Exercises 1 and 2 in models.py first: this file uses those models.

Start the server:

    uv run fastapi dev main.py

Then open http://127.0.0.1:8000/docs to try every endpoint in the browser
(or use Postman / curl). Check your progress with:

    uv run pytest

REST cheat sheet for this lab:

    Method  Path              Meaning                  Success   Errors
    GET     /plants           list all plants          200
    GET     /plants/{id}      read one plant           200       404
    POST    /plants           add a plant              201       422
    PUT     /plants/{id}      replace a whole plant    200       404, 422
    DELETE  /plants/{id}      remove a plant           204       404
    PATCH   /plants/{id}      change some fields       200       404, 422   (bonus)

You never have to write the 422 errors yourself: FastAPI returns 422
automatically when the request doesn't fit your Pydantic model.

Official documentation (with lots of examples):
    FastAPI tutorial:   https://fastapi.tiangolo.com/tutorial/first-steps/
    HTTP status codes:  https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
"""

from datetime import date, timedelta
from operator import ne
from optparse import Values

from fastapi import FastAPI, HTTPException, Query, status

from models import Plant, PlantCreate, PlantUpdate

app = FastAPI(title="Houseplant API")

# Our "database": maps a plant's id to the Plant, e.g. {1: Plant(id=1, ...)}.
# It lives in memory, so it is empty again every time the server restarts.
plants: dict[int, Plant] = {}

def see_plants() -> None:
    global plants 
    plants.clear()
    plants[1] = Plant(
        id=1,
        name="Monstera",
        species="Monstera deliciosa",
        water_every_days=10,
        last_watered=date.today() - timedelta(2),  # next watering in 8 days
        tags=["tropical"],
    )
    plants[2] = Plant(
        id=2,
        name="Aloe",
        indoor=False,
        water_every_days=14,
        last_watered=date.today() - timedelta(20),  # should have been watered 6 days ago!
        tags=["succulent"],
    )


# EXAMPLE (already done): list all plants
#   GET /plants returns 200 and a JSON list with every stored plant.
#
#   @app.get("/plants")   connects the method GET and the path /plants to
#                         this function. 200 OK is the default status code.
#   -> list[Plant]        tells FastAPI what we return: it turns the Plant
#                         objects into JSON and documents them in /docs.
#   Docs: https://fastapi.tiangolo.com/tutorial/first-steps/
#         https://fastapi.tiangolo.com/tutorial/response-model/#return-type-and-data-filtering
@app.get("/plants")
async def list_plants() -> list[Plant]:
    return list(plants.values())

# @app.get("/plants/{plant_id}",status_code=status.HTTP_200_OK)
# async def list_plants(plant_id: int, indoor: bool | None = False, tags: list | None = None):
#     plantId = {"plant_id":plant_id, "indoor": indoor, "tags": tags }
#     return plantId



# Exercise 3: Read one plant
#   GET /plants/{plant_id} returns 200 and the plant.
#   {plant_id} in the path is passed to the function as `plant_id`, and
#   FastAPI already checks that it is an int.
#   If there is no plant with that id, respond 404 with the message
#   "Plant not found":
#       raise HTTPException(status_code=404, detail="Plant not found")
#
#   Tip: you will need "find the plant or 404" in Exercises 5 and 6 too.
#   Put it in a small helper function, get_plant_or_404(plant_id), and reuse it.


async def get_plant_or_404(plant_id):
    plant = plants.get(plant_id)
    if plant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plant not found")
    return plant
#
#   Docs: https://fastapi.tiangolo.com/tutorial/path-params/
#         https://fastapi.tiangolo.com/tutorial/handling-errors/#use-httpexception
#         https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status#404_not_found
@app.get("/plants/{plant_id}")
async def get_plant(plant_id: int) -> Plant:
    return await get_plant_or_404(plant_id)


# Exercise 4: Add a plant
#   POST /plants with a PlantCreate body. FastAPI reads the JSON body,
#   validates it with PlantCreate and gives you the result as `plant_in`.
#   * The SERVER picks the id (the client never sends one): use one more
#     than the biggest id in use, or 1 when there are no plants yet.
#       Hint: max(plants, default=0) + 1
#   * Build the Plant, store it in `plants` and return it.
#       Hint: Plant(id=new_id, **plant_in.model_dump())
#   * A successful create must answer 201 Created, not 200.
#       Hint: add status_code=status.HTTP_201_CREATED to the decorator.
#
#   Docs: https://fastapi.tiangolo.com/tutorial/body/
#         https://fastapi.tiangolo.com/tutorial/response-status-code/
#         https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status#201_created
@app.post("/plants", status_code = status.HTTP_201_CREATED)
async def create_plant(plant_in: PlantCreate) -> Plant:
    new_id = max(plants, default=0) + 1
    plant = Plant(id = new_id, **plant_in.model_dump())
    plants[new_id] = plant
    return plant
   
        
    



# Exercise 5: Replace a plant
#   PUT /plants/{plant_id} with a PlantCreate body replaces the WHOLE plant.
#   * 404 "Plant not found" if the id does not exist.
#   * The id comes from the URL and never changes.
#   * Return the new plant with 200.
#
#   Docs: https://fastapi.tiangolo.com/tutorial/body-updates/#update-replacing-with-put
@app.put("/plants/{plant_id}")
async def replace_plant(plant_id: int, plant_in: PlantCreate) -> Plant:
    await get_plant_or_404(plant_id)
    plant = Plant(id = plant_id, **plant_in.model_dump())
    plants[plant_id] = plant
    return plant


# Exercise 6: Remove a plant. Now YOU write the whole endpoint!
#   DELETE /plants/{plant_id}
#   * 404 "Plant not found" if the id does not exist.
#   * On success answer 204 No Content, with an empty body. Your function
#     should return nothing, and the decorator needs the right status_code.
#   Hint: look at the endpoints above: @app.delete(...) works the same way.

@app.delete("/plants/{plant_id}", status_code = status.HTTP_204_NO_CONTENT)
async def delete_plant(plant_id: int):
    await get_plant_or_404(plant_id)
    plants.pop(plant_id)
#
#   Docs: https://fastapi.tiangolo.com/tutorial/sql-databases/#delete-a-hero
#         (a complete DELETE endpoint; it uses a database, we use our dict)
#         https://fastapi.tiangolo.com/tutorial/response-status-code/
#         https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status#204_no_content


# That's the whole REST API! Everything below is bonus.
# Start with Bonus 1-3 in models.py.


# BONUS 4: Partially update a plant (needs PlantUpdate from Bonus 3)
#   PATCH /plants/{plant_id} with a PlantUpdate body.
#   This is how the app records "I just watered my Monstera":
#       PATCH /plants/1   {"last_watered": "2026-10-01"}
#   * Only the fields the client sent change; all others stay the same.
#   * 404 "Plant not found" if the id does not exist.
#   * Return the updated plant with 200.
#   Hints: @app.patch(...)
#          changes.model_dump(exclude_unset=True) gives only the sent fields
#          stored_plant.model_copy(update={...}) makes an updated copy
@app.patch("/plants/{plant_id}")
async def patch_plant(plant_id: int, update_plant:PlantUpdate):
    await get_plant_or_404(plant_id)
    changes = update_plant.model_dump(exclude_unset=True)
    plants[plant_id] = plants[plant_id].model_copy(update=changes)
    return plants[plant_id]
#
#   Docs: https://fastapi.tiangolo.com/tutorial/body-updates/#partial-updates-with-patch
#         (this page shows both exclude_unset and model_copy step by step)


@app.post("/plants/{plant_id}/water", status_code= status.HTTP_200_OK)
async def water_plant(plant_id: int) -> Plant:
    plant = await get_plant_or_404(plant_id)
    plant = plant.model_copy(update =  {"last_watered":date.today()})
    plants[plant_id] = plant
    return plant


@app.get("/tags")
async def list_tags() - > list[str]:
    tags =set[str]()
    for plant in plants.values():   
        tags.update(plant.tags)
    return list[str](tags)


@app.patch("/tags/{tag}")
async def update_tags(tag:str, new_tag:str) -> None:
    for plant in plants.values():
        if tag in plant.tags:
            plant.tags = [new_tag if t == tag else t for t in plant.tags]
    return None 

# BONUS 5: Filter the list with query parameters
#   Go back to list_plants (the EXAMPLE at the top) and add three OPTIONAL
#   filters:
#     GET /plants?indoor=false           only plants that live outdoors
#     GET /plants?tag=succulent          only plants with the tag "succulent"
#     GET /plants?due_within_days=3      only plants that need water in the
#                                        next 3 days (0 = today or overdue)
#   They can be combined: /plants?indoor=true&due_within_days=0
#   Any function parameter that is not in the path becomes a query parameter.
#
#   due_within_days must be between 0 and 60, otherwise FastAPI answers 422:
#     due_within_days: int | None = Query(default=None, ge=0, le=60)
#
#   When does a plant need water next?
#     * never watered (last_watered is None): today
#     * otherwise: last_watered + timedelta(days=water_every_days)
#   It is "due within N days" if that date is on or before
#     date.today() + timedelta(days=N)
#
#   Docs: https://fastapi.tiangolo.com/tutorial/query-params/#optional-parameters
#         https://fastapi.tiangolo.com/tutorial/path-params-numeric-validations/#number-validations-greater-than-and-less-than-or-equal
#         (that page shows ge/le on Path(...); Query(...) takes the same arguments)
#         https://docs.python.org/3/library/datetime.html#timedelta-objects
