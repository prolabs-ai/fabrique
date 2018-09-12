import jsonschema
import json
import importlib.machinery
import types

from fabrique.engines import Model,Rules,Decision,FeatureExtractor

# Define JSON schema for the pipeline

pipeline_schema = {
 "id":"PipelineSchema",
 "$schema": "http://json-schema.org/draft-07/schema#",
 "required":["description",
             "nodes",
             "transitions"],

  "type":"object",
  "properties":
  {
  "description" : {"type" : "string"},

  "nodes": {"type":"array",
            "items":
            {
              "anyOf":[
                  {"type":"object",
                    "properties":
                    {
                     "id":{"type":"string"},
                     "type":{"type":"string"},
                     "file":{"type":"string"},
                     "class":{"type":"string"},
                    },
                    "required":["id","type","file","class"]
                  },
                  {"type":"object",
                    "properties":
                    {
                     "id":{"type":"string"},
                     "type":{"type":"string"},
                     "schema":{"type":"string"},
                    },
                    "required":["id","type","schema"]
                  }]
            }
           },

  "transitions":{"type":"array",
                 "items":
                 {
                    "type":"object",
                    "properties":
                    {
                      "from":{"type":"string"},
                      "to":{"type":"string"},
                      "condition":{"type":"string"}
                    },
                    "required":["from","to"]
                 }
                }
  }
}

# Pipeline validation
def validate_pipeline(pipeline):

  # First we use the pipeline schema to validate the JSON
  jsonschema.validate(pipeline, pipeline_schema)

  # Now we'll check that all references in the transitions are defined, and there is at least one node in the graph
  nodes = {}
  for  n in pipeline["nodes"]:
    if n["id"] in nodes:
      raise Exception("Node with id '%s' already in the graph" % n["id"])
    nodes[n["id"]] = n

  if not nodes:
    raise Exception("No nodes in the pipeline")

  transitions = [t for t in pipeline["transitions"]]

  for t in transitions:
    if not t["from"] in nodes or not t["to"] in nodes:
      raise Exception("Transition references a node '%s' that is not present in the node list" % t["from"])

  # Check the topology of the graph, make sure its a tree
  curr_node = list(nodes.keys())[0]
  visited = {curr_node}
  while [t for t in transitions if t["to"]==curr_node]:
    t = [t for t in transitions if t["to"]==curr_node][0]
    if t["from"] in visited:
      raise Exception("Graph is not a simple tree, multiple transitions to node '%s'" % t["from"])

    curr_node = t["from"]
    visited = visited.union({t["from"]})

  visited = {curr_node}
  stack = [curr_node]
  while stack:
    curr_node = stack.pop()
    for trans in [t for t in transitions if t["from"]==curr_node]:
      if trans["to"] in visited:
        raise Exception("Graph is not a simple tree, multiple transitions to node '%s'" % t["to"])

      stack.append(trans["to"])
      visited = visited.union( {trans["to"]} )

  for n in nodes:
    if not n in visited:
      raise Exception("Graph is not connected, node '%s' is not reached" % n)

  # Check individual nodes: referenced files should be there, classes should be derived correctly
  for n in nodes:
    if nodes[n]["type"] not in ["SchemaValidator","Rules","Decision","Model","FeatureExtractor"]:
      raise Exception("Unknown type of pipeline node, node '%s', type '%s'" % (nodes[n]["id"],nodes[n]["type"]))

    # If this is a schema validator, check that the schema file can be opened and its in JSON format
    if nodes[n]["type"] == "SchemaValidator":
      try:
        json.load(open(nodes[n]["schema"]))
      except:
        raise Exception("Cannot open schema file for node '%s', file '%s'" % (nodes[n]["id"], nodes[n]["schema"]))

    # Otherwise, its one of the engines. Open the engine file, load the class and check that its a subclass
    # of the correct engine class
    else:
      loader = importlib.machinery.SourceFileLoader('model', nodes[n]["file"])
      mod = types.ModuleType(loader.name)
      loader.exec_module(mod)
      engine = eval("mod." + nodes[n]["class"] + "()")
      
      instance_map = {"Model":Model, "Rules":Rules, "Decision":Decision, "FeatureExtractor":FeatureExtractor}
      if not isinstance(engine, instance_map[nodes[n]["type"]]):
        raise Exception("Engine in the node '%s' is not of type '%s'" % (nodes[n]["id"], nodes[n]["type"] ))

      # Check that conditional transitions are well-defined
      trans = [t for t in transitions if t["from"]==nodes[n]["id"]]
      if any( ["condition" in t for t in trans] ):
        if not len(trans)==2:
          raise Exception("There should always be two conditional transitions, node '%s'" % nodes[n]["id"])

        for t in trans:
          if not t["condition"] in ["True","False"]:
            raise Exception("Conditional transitions can be either True or False, node '%s'" % nodes[n]["id"])

        if eval(trans[1]["condition"]) == eval(trans[0]["condition"]):
          raise Exception("Second transition from node '%s' cannot be '%s'" % (nodes[n]["id"], trans[1]["condition"]))
