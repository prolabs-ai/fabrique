import jsonschema
import json

class SchemaValidator():
  def __init__(self,schema):
    self.schema = json.load(open(schema))

  def get_result(self,data):
    jsonschema.validate(data,self.schema)
    return data
