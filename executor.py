import importlib.machinery
import types
import sys
import json

from fabrique.engines import Rules, Model,Decision,FeatureExtractor

# Python pipeline executor
class Executor():

  # Basic execution method. This method assumes the pipeline
  # has been validated already. Will break on unvalidated
  # pipelines

  def execute(self,pipeline_spec_file,data_file):
    data = json.load(data_file)
    pipeline = json.load(pipeline_spec_file)
    
    nodes = { x["node-id"]:x for x in pipeline["nodes"] }

    start_node_id = pipeline["transitions"][0]["from"]
    while start_node_id in [p["to"] for p in pipeline["transitions"]]:
      start_node_id = next([p["from"] for p in pipeline["transitions"] if p["to"]==start_node])

    for curr_data in data:
      curr_node_id = start_node_id
      curr_engine = self.get_engine(nodes[curr_node_id])
      result = None
      
      while curr_engine:
        print("Processing:",nodes[curr_node_id])

        if isinstance(curr_engine,Model):
          curr_engine.load_model(nodes[curr_node_id].get("model_file"))
        if isinstance(curr_engine,Decision):
          result = curr_engine.get_result(curr_data,result)
        elif isinstance(curr_engine,FeatureExtractor):
          curr_data = curr_engine.get_result(curr_data)
        else:
          result = curr_engine.get_result(curr_data)

        next_node_id = None
        for t in [p for p in pipeline["transitions"] if p["from"]==curr_node_id]:
          if "condition" in t:
            if eval(t["condition"]) == result:
              next_node_id = t["to"]
          else:
            next_node_id = t["to"]

        if not next_node_id and not isinstance(curr_engine,Decision):
          print("Current node:",curr_node_id)
          print(type(curr_engine))
          raise Exception("Decision node in the pipeline not reached!")

        if not next_node_id:
          break

        curr_node_id = next_node_id
        curr_engine = self.get_engine(nodes[curr_node_id])

      print("Pipeline finished, result:", result)

  def get_engine(self,node):
    loader = importlib.machinery.SourceFileLoader('model', node["file"])
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)
    engine = eval("mod." + node["class"] + "()")
    return engine


if __name__=="__main__":
  ex = Executor()
  ex.execute(open(sys.argv[1]), open(sys.argv[2]))
