import os
import json
import csv
import datetime
import hashlib
from typing import Dict, Any

class ExperimentHarness:
    def __init__(self, experiment_dir: str = 'experiments'):
        """
        Initialize the ExperimentHarness.

        Args:
            experiment_dir (str): Directory to store experiment logs and results.
        """
        self.experiment_dir = experiment_dir
        os.makedirs(experiment_dir, exist_ok=True)

    def run_experiment(self, experiment_fn: callable = (), parameters: Dict[str, Any] = None):
        """
        Run an experiment and log the results.

        Args:
            experiment_fn (callable): The experiment function to run.
            config (ExperimentConfig): Experiment configuration.
            parameters (dict): Parameters specific to this experiment.
        """
        # Create a timestamped experiment directory
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        experiment_name = f'experiment_{hashlib.md5(timestamp.encode()).hexdigest()}'
        experiment_path = os.path.join(self.experiment_dir, experiment_name)
        os.makedirs(experiment_path)

        # Log parameters to a JSON file
        parameters_path = os.path.join(experiment_path, 'parameters.json')
        with open(parameters_path, 'w') as param_file:
            json.dump(parameters, param_file, indent=4)

        # Run the experiment and capture its output
        experiment_output = experiment_fn(parameters)

        # Log experiment output to a JSON file
        output_path = os.path.join(experiment_path, 'output.json')
        with open(output_path, 'w') as output_file:
            json.dump(experiment_output, output_file, indent=4)

        # Log experiment information to a CSV file
        csv_path = os.path.join(self.experiment_dir, 'experiments.csv')
        experiment_info = {
            'experiment_name': experiment_name,
            'timestamp': timestamp,
            'parameters_path': parameters_path,
            'output_path': output_path,
        }

        # Append experiment information to the CSV file
        with open(csv_path, 'a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=experiment_info.keys())
            if os.stat(csv_path).st_size == 0:
                writer.writeheader()
            writer.writerow(experiment_info)

if __name__ == "__main__":
    experiment_parameters = {'param1': 42, 'param2': 'abc'}  # Customize as needed
    # Example experiment function
    def my_experiment(config: Dict[str, Any] = None):
        # Your experiment code here
        print(f"Running experiment with config: {config}")
        return {'result': 'some_data'}

    # Example usage
    harness = ExperimentHarness(experiment_dir='my_experiments')
    harness.run_experiment(my_experiment, experiment_parameters)
