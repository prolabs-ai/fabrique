# Rules engine applies rules to the data
# which result in a boolean outcome

class Rules():

  def get_result(self,data):
    raise Exception("This method needs to be defined in a subclass")

# Decision class provides a decision that is based on the result
# of the previous stage and data

class Decision():

  def get_result(self,data,result):
    raise Exception("This method needs to be defined in a subclass")

# Model class provides a method to deserialize a model from binary
# format and execute a model on the data

class Model():

  def load_model(self,path):
    pass

  def get_result(self,data):
    raise Exception("This method needs to be defined in a subclass")

# Feature extractor extracts features from data and adds them
# to the output

class FeatureExtractor():

  def get_features(self,data):
    raise Exception("This method needs to be defined in a subclass")

