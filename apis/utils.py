from jsonschema import validate, exceptions


def validate_json(json_body, schema):
    err = None
    try:
        validate(instance=json_body, schema=schema)
    except exceptions.SchemaError as err:
        return False, err
    except exceptions.ValidationError as err:
        return False, err
    return True, err
