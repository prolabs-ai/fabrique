#!/usr/bin/env python

import importlib.machinery
import types
import sys
import json
import traceback

from fabrique.engines import Rules, Model,Decision,FeatureExtractor
from fabrique.validators import SchemaValidator
from fabrique.pipeline import validate_pipeline

# Python pipeline executor
class Executor():

  # Basic execution method. This method assumes the pipeline
  # has been validated already. Will break on unvalidated
  # pipelines

  def execute(self,pipeline_spec_file,data_file):
    data = json.load(data_file)
    pipeline = json.load(pipeline_spec_file)
    validate_pipeline(pipeline)
    
    nodes = { x["id"]:x for x in pipeline["nodes"] }

    start_node_id = pipeline["transitions"][0]["from"]
    while start_node_id in [p["to"] for p in pipeline["transitions"]]:
      start_node_id = next([p["from"] for p in pipeline["transitions"] if p["to"]==start_node])

    for curr_data in data:
      curr_node_id = start_node_id
      curr_engine = None
      try:
        curr_engine = self.get_engine(nodes[curr_node_id])
      except Exception as e:
        msg = traceback.format_exc()
        return {"error": msg}

      result = None
      
      while curr_engine:
        print("Processing:",nodes[curr_node_id])

        try:
          if isinstance(curr_engine,Model):
            curr_engine.load_model(nodes[curr_node_id].get("model_file"))

          if isinstance(curr_engine,Decision):
            result = curr_engine.get_result(curr_data,result)
          elif isinstance(curr_engine,FeatureExtractor):
            curr_data = curr_engine.get_result(curr_data)
          else:
            result = curr_engine.get_result(curr_data)

        except Exception as e:
          msg = traceback.format_exc()
          yield {"error": msg}

        next_node_id = None
        for t in [p for p in pipeline["transitions"] if p["from"]==curr_node_id]:
          if "condition" in t:
            if eval(t["condition"]) == result:
              next_node_id = t["to"]
          else:
            next_node_id = t["to"]

        if not next_node_id:
          break

        curr_node_id = next_node_id
        curr_engine = self.get_engine(nodes[curr_node_id])

      if type(result) != dict:
        result = {"result":result}
 
      yield result

  def get_engine(self,node):
    if node["type"] == "SchemaValidator":
      return SchemaValidator(node["schema"])

    elif node["type"] not in ["Rules","Decision","Model","FeatureExtractor"]:
      raise Exception("Unknown type of pipeline node: %s" % node["type"])

    loader = importlib.machinery.SourceFileLoader('model', node["file"])
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)
    engine = eval("mod." + node["class"] + "()")
    return engine
