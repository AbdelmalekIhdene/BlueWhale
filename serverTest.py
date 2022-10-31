import unittest
import server
import numpy as np
import statistics

import types_pb2 as pbtypes

class serverTest(unittest.TestCase):

    def test_loadCSVDataset_withDVDtrainingCSV(self):
        dataset = server.loadCSVDataset("DVD-training.csv")
        self.assertEqual(len(dataset), 4)
        self.assertIsNotNone(dataset[0][0])

    def test_loadCSVDataset_withEmptyCSV(self):
        dataset = server.loadCSVDataset("empty.csv")
        self.assertEqual(len(dataset), 4)
        self.assertEqual(dataset[0], [])

    def test_calculateAnalytics(self):
        testSamples = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        sum = 0
        for sample in testSamples:
            sum = sum + sample
            average = sum / len(testSamples)
        self.assertEqual(server.calculateAnalytics(testSamples, len(testSamples), pbtypes.AnalyticsType.T10P), np.percentile(testSamples, 10))
        self.assertEqual(server.calculateAnalytics(testSamples, len(testSamples), pbtypes.AnalyticsType.T50P), np.percentile(testSamples, 50))
        self.assertEqual(server.calculateAnalytics(testSamples, len(testSamples), pbtypes.AnalyticsType.T95P), np.percentile(testSamples, 95))
        self.assertEqual(server.calculateAnalytics(testSamples, len(testSamples), pbtypes.AnalyticsType.T99P), np.percentile(testSamples, 99))
        self.assertEqual(server.calculateAnalytics(testSamples, len(testSamples), pbtypes.AnalyticsType.AVG), average)
        self.assertEqual(server.calculateAnalytics(testSamples, len(testSamples), pbtypes.AnalyticsType.STD), statistics.stdev(testSamples))
        self.assertEqual(server.calculateAnalytics(testSamples, len(testSamples), pbtypes.AnalyticsType.MAX), 10)
        self.assertEqual(server.calculateAnalytics(testSamples, len(testSamples), pbtypes.AnalyticsType.MIN), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)