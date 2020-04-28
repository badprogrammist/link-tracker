"""
Json validation
"""
import functools
import json
import os

import jsonschema
from flask import request

from context import app_ctx
from .exceptions import BadRequest


class ApiDataValidator:
    """
    Validates json by given schema
    """

    def __init__(self, schemas_path):
        """
        :param schemas_path: root dir of schemas
        """
        self.schemas_path = schemas_path
        self._cache = dict()

    def get_schema(self, name):
        """
        Get validation schema
        :param name: name of file
        :return: schema as dict
        """
        if name not in self._cache:
            path = os.path.join(self.schemas_path,
                                f'{name}.json')
            with open(path) as file:
                schema = json.load(file)
                self._cache[name] = schema

        return self._cache[name]

    def validate(self, data, schema_name):
        """
        Validates json data by given schema
        :param data: json
        :param schema_name: filename
        :return: None
        """
        schema = self.get_schema(schema_name)
        try:
            jsonschema.validate(data, schema)
            return None
        except jsonschema.ValidationError as err:
            return str(err)


class ValidationError(BadRequest):
    pass


def validate(schema_name):
    """
    Decorator for applying validation
    :param schema_name: filename of schema
    """

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
