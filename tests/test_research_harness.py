import os
import json
import csv
import time
import unittest
from typing import Dict, Any
from research_harness import ExperimentHarness

class TestExperimentHarness(unittest.TestCase):
    def setUp(self):
        self.experiment_dir = 'test_experiments'
        self.harness = ExperimentHarness(experiment_dir=self.experiment_dir)

    def tearDown(self):
        # Clean up test experiment directories
        for root, dirs, files in os.walk(self.experiment_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.experiment_dir)

    def test_run_experiment(self):
        # Define a sample experiment function
        def sample_experiment(config: Dict[str, Any] = None):
            return {'result': 'sample_data'}

        # Define sample experiment configuration and parameters
        experiment_parameters = {'param1': 42, 'param2': 'abc'}

        # Run the experiment using the harness
        self.harness.run_experiment(sample_experiment, experiment_parameters)

        # Verify that the experiment directory exists
        self.assertTrue(os.path.exists(self.experiment_dir))

        # Verify that parameters and output files are created
        experiment_folders = os.listdir(self.experiment_dir)

        self.assertEqual(len(experiment_folders), 2)
        experiment_folders.sort()
        experiment_folder = experiment_folders[0]

        parameters_path = os.path.join(self.experiment_dir, experiment_folder, 'parameters.json')
        self.assertTrue(os.path.exists(parameters_path))

        output_path = os.path.join(self.experiment_dir, experiment_folder, 'output.json')
        self.assertTrue(os.path.exists(output_path))

        # Verify that experiment information is logged in the CSV file
        csv_path = os.path.join(self.experiment_dir, 'experiments.csv')
        self.assertTrue(os.path.exists(csv_path))

        with open(csv_path, 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            experiment_info = rows[0]

            # Verify that experiment information is correctly logged
            self.assertEqual(experiment_info['experiment_name'], experiment_folder)
            self.assertTrue(experiment_info['timestamp'])
            self.assertEqual(experiment_info['parameters_path'], parameters_path)
            self.assertEqual(experiment_info['output_path'], output_path)

        # Verify the content of parameters and output JSON files
        with open(parameters_path, 'r') as param_file:
            parameters = json.load(param_file)
            self.assertEqual(parameters, experiment_parameters)

        with open(output_path, 'r') as output_file:
            output_data = json.load(output_file)
            self.assertEqual(output_data, {'result': 'sample_data'})

if __name__ == '__main__':
    unittest.main()
