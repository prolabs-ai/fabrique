from fabrique.engines import Decision,Rules,Model,FeatureExtractor
import random

# Simple blacklist ruleset

class BlacklistRules(Rules):
  def get_result(self,data):
    if data['doc_num'] == 12345:
      return False
    return True

# Return a decision to the consumer of the service

class BlacklistReject(Decision):
  def get_result(self,data, result):
    return {'decision':False, 'reason':'Client in the blacklist'}

# Basic scoring model, score randomly

class ScoringModel(Model):
  def get_result(self,data):
    return random.random()

# Decision, based on scoring

class ModelDecision(Decision):
  def get_result(self,data,result):
    if result < 0.5:
      return {'decision':False, 'reason':'Low score', 'score':result}
    else:
      return {'decision':True, 'reason':'High score', 'score':result}
