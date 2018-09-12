This is a client library for Fabrique.ai to test machine learning pipelines,
before submitting them to Fabrique

Build a pipeline from the following engines (you need to override the _get_result_ methods):

**Rules:

   A simple engine that computes some rules and returns a True/False result. 
   
**FeatureExtractor:

   Extracts features from the data and returns enriched data.
   
**Model:

   An engine that loads a model from binary representation and applies it to incoming data.
   You will need to override both _get_result_ and _load_model_ methods
   
**Decision:

   An engine that returns a final decision in JSON format.
   
There is also a prebuilt schema validation engine that can be used to validate incoming
data with JSON Schema.
   
