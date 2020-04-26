import functools
import json
import os

import jsonschema
from flask import request

from context import app_ctx
from .exceptions import BadRequest


class ApiDataValidator:
    def __init__(self, schemas_path):
        self.schemas_path = schemas_path
        self._cache = dict()

    def get_schema(self, name):
        if name not in self._cache:
            path = os.path.join(self.schemas_path,
                                f'{name}.json')
            with open(path) as file:
                schema = json.load(file)
                self._cache[name] = schema

        return self._cache[name]

    def validate(self, data, schema_name):
        schema = self.get_schema(schema_name)
        try:
            jsonschema.validate(data, schema)
            return None
        except jsonschema.ValidationError as err:
            return str(err)


class ValidationError(BadRequest):
    pass


def validate(schema_name):
    def wrapper(func):
        @functools.wraps(func)
        def decorated(*args, **kwargs):
            validator = app_ctx.validator
            error = validator.validate(request.json, schema_name)
            if error:
                raise ValidationError(error)
            return func(*args, **kwargs)

        return decorated

    return wrapper
