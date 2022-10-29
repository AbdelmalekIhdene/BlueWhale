import os
import pyinputplus as pyip
import requests
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse as JSONParse
from decouple import config

import types_pb2 as pbtypes

print("///////////////////////////////////////////////////////////////")
print("Welcome to the RFW Request Generator & Client [RFWRGC]")
print("By Abdelmalek Ihdene & Jonathan Perlman & Nithujan Tharmalingam")
print("///////////////////////////////////////////////////////////////")
print("The client will:")
print("1. Prompt the user with a set of inquiries.")
print("2. Generate an HTTP request from the resulting answers.")
print("3. Send that request over to the server.")
print("4. Display the resulting RFD payload.")
print("///////////////////////////////////////////////////////////////")

def inputMenuWrapper(prompt, enum):
  return pyip.inputMenu(prompt=prompt, choices=enum.keys())

request = pbtypes.RFW()
request.Id = pyip.inputInt("Enter the ID of the RFW:\n")
request.benchmarkType = inputMenuWrapper("\nEnter benchmark type:\n", pbtypes.BenchmarkType)
request.workloadMetric = inputMenuWrapper("\nEnter workload metric:\n", pbtypes.WorkloadMetric)
request.sampleCount = pyip.inputInt("\nEnter the sample count:\n", greaterThan=0)
request.batchId = pyip.inputInt("\nEnter the batch ID:\n", greaterThan=0)
request.batchCount = pyip.inputInt("\nEnter the batch count:\n", greaterThan=0)
request.dataType = inputMenuWrapper("\nEnter data type:\n", pbtypes.DataType)
request.analyticsType = inputMenuWrapper("\nEnter the analytics type:\n", pbtypes.AnalyticsType)
isDataJSON = pyip.inputMenu(prompt="\nWhat should be the format of the request body?\n", choices=["JSON", "Protobuf"]) == "JSON"

data = MessageToJson(request, including_default_value_fields=True) if isDataJSON else request.SerializeToString()
print("\nResulting request body:\n" + str(data))

headers = {
  "Content-Type": "application/json" if isDataJSON else "application/x-protobuf" 
}
RFD = None
print("\nPosting to server: " + config("SERVER_URL"))
response = requests.post(url=config("SERVER_URL"), data=data, headers=headers)
print("Received response [" + str(response.status_code) + "] back...")

if response.status_code == 200:
  print("Response content:\n" + str(response.content))
  if response.headers["Content-Type"] == 'application/json':
    data = response.content
    RFD = JSONParse(text=data, message=pbtypes.RFD())
  else:
    data = response.content
    RFD = pbtypes.RFD()
    RFD.ParseFromString(data)
    
  print("\nRFD:")
  print("ID: " + str(RFD.Id))
  print("Last batch ID: " + str(RFD.lastBatchId))
  print("Samples: " + str(RFD.samples))
  print("Analytics: " + str(RFD.analyticsValue))
elif response.status_code == 500:
  print("Response error:\n" + str(response.content.decode()))
