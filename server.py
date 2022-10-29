import csv
import statistics

import numpy as np
from flask import Flask, request, Response
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse as JSONParse

import types_pb2 as pbtypes

def loadCSVDataset(path):
  with open(path, newline='') as csvfile:
    reader = csv.reader(csvfile)
    series = [[], [], [], []]
    skippedHeader = False
    for row in reader:
      if skippedHeader == False:
        skippedHeader = True
        continue
      series[0].append(float(row[0]))
      series[1].append(float(row[1]))
      series[2].append(float(row[2]))
      series[3].append(float(row[3]))
    return series

DVDSTORE_TRAINING = loadCSVDataset("DVD-training.csv")
DVDSTORE_TESTING = loadCSVDataset("DVD-testing.csv")
NDBENCH_TRAINING = loadCSVDataset("NDBench-training.csv")
NDBENCH_TESTING = loadCSVDataset("NDBench-testing.csv")

app = Flask(__name__)

def calculateAnalytics(samples, totalSampleCount, analyticsType):
  sum = 0
  for sample in samples:
    sum = sum + sample
  average = sum / totalSampleCount
  sorted_samples = sorted(samples, key=float)
  min = sorted_samples[0]
  max = sorted_samples[totalSampleCount - 1]
  np_samples = np.array(samples)
  if analyticsType == pbtypes.AnalyticsType.T10P:
    return np.percentile(np_samples, 10)
  elif analyticsType == pbtypes.AnalyticsType.T50P:
    return np.percentile(np_samples, 50)
  elif analyticsType == pbtypes.AnalyticsType.T95P:
    return np.percentile(np_samples, 95)
  elif analyticsType == pbtypes.AnalyticsType.T99P:
    return np.percentile(np_samples, 99)
  elif analyticsType == pbtypes.AnalyticsType.AVG:
    return average
  elif analyticsType == pbtypes.AnalyticsType.STD:
    return statistics.stdev(sample)
  elif analyticsType == pbtypes.AnalyticsType.MAX:
    return max
  elif analyticsType == pbtypes.AnalyticsType.MIN:
    return min

def generateRFD(RFW):
  RFD = pbtypes.RFD()
  RFD.Id = RFW.Id
  RFD.lastBatchId = RFW.batchId + RFW.batchCount - 1
  
  series = None
  if RFW.benchmarkType == pbtypes.BenchmarkType.DVDSTORE and RFW.dataType == pbtypes.DataType.TRAINING:
    series = DVDSTORE_TRAINING
  elif RFW.benchmarkType == pbtypes.BenchmarkType.DVDSTORE and RFW.dataType == pbtypes.DataType.TESTING:
    series = DVDSTORE_TESTING
  elif RFW.benchmarkType == pbtypes.BenchmarkType.NDBENCH and RFW.dataType == pbtypes.DataType.TRAINING:
    series = NDBENCH_TRAINING
  elif RFW.benchmarkType == pbtypes.BenchmarkType.NDBENCH and RFW.dataType == pbtypes.DataType.TESTING:
    series = NDBENCH_TESTING
  serie = series[RFW.workloadMetric]

  startingOffset = (RFW.batchId - 1) * RFW.sampleCount
  totalSampleCount = RFW.batchCount * RFW.sampleCount
  endingOffset = startingOffset+totalSampleCount-1

  samples = serie[startingOffset:startingOffset+totalSampleCount]
  RFD.samples.extend(samples)
  RFD.analyticsValue = calculateAnalytics(samples, totalSampleCount, RFW.analyticsType)
  return RFD

@app.route("/", methods=["POST"])
def index():
  RFW = None
  isJSON = request.mimetype == "application/json"
  if isJSON:
    data = request.get_data()
    RFW = JSONParse(text=data, message=pbtypes.RFW())
  else:
    data = request.get_data()
    RFW = pbtypes.RFW()
    RFW.ParseFromString(data)
  try:
    RFD = generateRFD(RFW)
  except IndexError:
    response = Response("Accessing out-of-bound dataset indexes")
    response.status = 500
    return response
  response = Response(MessageToJson(RFD, including_default_value_fields=True) if isJSON else RFD.SerializeToString())
  response.headers["Content-Type"] = request.mimetype
  response.status = 200
  return response

app.run(host='0.0.0.0', port=8080)
