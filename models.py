"""
Lab 7, Part 1: Pydantic models
==============================

We are building an API that keeps track of your houseplants and when they
need water.

A Pydantic model describes what valid data looks like. When you create a
model from some data (for example the JSON body of a request), Pydantic:

  * converts values to the right type when it safely can ("7" -> 7),
  * checks every rule you wrote down (length, range, ...),
  * raises a ValidationError listing everything that is wrong.

FastAPI uses these models to validate every request for you, so the better
your models are, the less checking code you write in your endpoints.

Check your progress at any time with:

    uv run pytest

Tip: try your models out in a Python shell while you work:

    uv run python
    >>> from models import PlantCreate
    >>> PlantCreate(name="Monstera")
    >>> PlantCreate(name="")

Official Pydantic documentation (with lots of examples):
    https://docs.pydantic.dev/latest/concepts/models/
"""

from datetime import date
from email.policy import default

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator
from typing import Annotated



def name_not_blank(value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("name must not be blank")
        return name

Name = Annotated[str, Field(min_length=1, max_length=50) , AfterValidator(name_not_blank)]

def watered_date_not_in_future(watered_date: date | None):
    if watered_date is None:
        return None
    if watered_date > date.today():
        raise ValueError("last_watered cannot be in the future")
    return watered_date

Date = Annotated[date | None , Field(default= None), AfterValidator(watered_date_not_in_future)]

# ---------------------------------------------------------------------------
# PlantCreate: the data a client sends when it adds a new plant.
# ---------------------------------------------------------------------------
class PlantCreate(BaseModel):

    model_config = ConfigDict(extra="forbid")
    # EXAMPLE (already done): the first two fields.
    #   name     a required str of 1 to 50 characters; Field(...) adds rules
    #   species  an optional str: it may be None, and is None when not sent
    #   Docs: https://docs.pydantic.dev/latest/concepts/models/#basic-model-usage
    #         https://docs.pydantic.dev/latest/concepts/fields/#string-constraints

    #= Field(min_length=1, max_length=50)
    name: Name #str = Field(min_length=1, max_length=50)
    species: str | None = None
    indoor: bool = True
    water_every_days: int = Field(gt = 0, le = 60, default =7)
    last_watered: Date #date | None = None
    tags: list = []

    # Exercise 1: More fields, types and rules
    #   Add two fields, following the example above:
    #     indoor            a bool, default True
    #     water_every_days  an int from 1 to 60 (inclusive), default 7
    #   Hint: Field(default=..., ge=..., le=...)   (ge = "greater or equal")
    #   Docs: https://docs.pydantic.dev/latest/concepts/fields/#default-values
    #         https://docs.pydantic.dev/latest/concepts/fields/#numeric-constraints
    #         https://docs.pydantic.dev/latest/concepts/conversion_table/
    #         (the last one shows which values Pydantic converts, e.g. "true" -> True)
    #
    # Exercise 2: Dates and lists
    #   Add two more fields:
    #     last_watered  a date or None, default None
    #                   (Pydantic turns the JSON string "2026-10-01" into a date)
    #     tags          a list of strings, default empty list []
    #                   e.g. ["succulent", "pet-safe"]
    #   Docs: https://docs.pydantic.dev/latest/api/standard_library_types/#datetimedate
    #         https://docs.pydantic.dev/latest/api/standard_library_types/#lists
    #
    # Now go to main.py for Part 2!

    # BONUS 1: Custom validators (do this after Part 2)
    #   a) Clean up the name: "  Monstera  " must become "Monstera".
    #      A name made only of spaces ("   ") must be rejected by raising
    #      ValueError("name must not be blank").
    #   b) You can't have watered a plant tomorrow: if last_watered is a date
    #      after date.today(), raise ValueError("last_watered cannot be in the future").
    #
    #   Write each one as a method inside this class, like this:
    #
    # @field_validator('name')
    # @classmethod
    # def name_not_blank(cls:PlantCreate, value: str) -> str:
    #         name = value.strip()
    #         if not name:
    #             raise ValueError("name must not be blank")
    #         return name

    # @field_validator('last_watered')
    # @classmethod
    # def watered_date_not_in_future(cls:PlantCreate, date: date | None):
    #     if date > date.today():
    #         raise ValueError("last_watered cannot be in the future")
    #     return date
    
    #
    #   Docs: https://docs.pydantic.dev/latest/concepts/validators/#field-validators
    #         https://docs.python.org/3/library/datetime.html#datetime.date.today
    #
    # BONUS 2: No unknown fields
    #   By default Pydantic silently IGNORES fields it does not know, so a
    #   typo like {"nmae": "Monstera"} goes unnoticed. Make PlantCreate reject
    #   unknown fields by adding this line to the class:
    #     model_config = ConfigDict(extra="forbid")
    #   Docs: https://docs.pydantic.dev/latest/concepts/models/#extra-data


# ---------------------------------------------------------------------------
# EXAMPLE (already done): Plant, a plant as stored and returned by the API.
#   A stored plant is exactly a PlantCreate plus an id chosen by the server.
#   Plant INHERITS from PlantCreate, so it gets all of its fields and rules
#   (including the ones you add) without copying them.
#   Docs: https://fastapi.tiangolo.com/tutorial/extra-models/#reduce-duplication
# ---------------------------------------------------------------------------
class Plant(PlantCreate):
    id: int


# ---------------------------------------------------------------------------
# BONUS 3: PlantUpdate, the body of a PATCH (partial update) request
#   With PATCH the client sends ONLY the fields it wants to change, for
#   example {"last_watered": "2026-10-01"} after watering a plant.
#   So here EVERY field is optional, default None:
#     name              str or None, still 1 to 50 characters when given
#     species           str or None
#     indoor            bool or None
#     water_every_days  int or None, still 1 to 60 when given
#     last_watered      date or None
#     tags              list of str or None
#   Unknown fields must be rejected here too (see Bonus 2).
#
#   Then try this in a Python shell and think about why it is useful:
#     >>> PlantUpdate(indoor=False).model_dump()
#     >>> PlantUpdate(indoor=False).model_dump(exclude_unset=True)
#
#   Docs: https://fastapi.tiangolo.com/tutorial/body-updates/#partial-updates-with-patch
#         https://docs.pydantic.dev/latest/concepts/serialization/#modelmodel_dump
# ---------------------------------------------------------------------------
class PlantUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name | None = None #str | None = Field(min_length=1, max_length=50, default=None)
    species: str | None = None
    indoor: bool | None = None
    water_every_days: int | None = Field(gt = 0, le = 60, default =None)
    last_watered: Date | None = None #date | None = None
    tags: list | None = None

    # @field_validator('name')
    # @classmethod
    # def name_not_blank(cls:PlantCreate, value: str | None) -> str:
    #     if value is None:
    #         return None
    #     name = value.strip()
    #     if not name:
    #         raise ValueError("name must not be blank")
    #     return name

    # @field_validator('last_watered')
    # @classmethod
    # def watered_date_not_in_future(cls:PlantCreate, date: date | None):
    #     if date is None:
    #         return None
    #     if date > date.today():
    #         raise ValueError("last_watered cannot be in the future")
    #     return date
   
