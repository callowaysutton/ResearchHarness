import os
import json
import csv
import datetime
import hashlib
from typing import Dict, Any
import multiprocessing
import time

class ExperimentConfig:
    def __init__(self, max_duration_seconds: int = 10, experiment_name: str = "experiment"):
        """
        Initialize the ExperimentConfig.

        Args:
            max_duration_seconds (int): Maximum time (in seconds) the experiment is allowed to run.
            experiment_name (str): Name of the experiment.
            data (dict): Data specific to this experiment.
        """
        self.max_duration_seconds = max_duration_seconds
        self.experiment_name = experiment_name

class ExperimentHarness:
    def __init__(self, experiment_dir: str = 'experiments'):
        """
        Initialize the ExperimentHarness.

        Args:
            experiment_dir (str): Directory to store experiment logs and results.
        """
        self.experiment_dir = experiment_dir
        os.makedirs(experiment_dir, exist_ok=True)

    def run_experiment(self, experiment_fn: callable = (), parameters: Dict[str, Any] = None, config: ExperimentConfig = None):
        """
        Run an experiment and log the results.

        Args:
            experiment_fn (callable): The experiment function to run.
            parameters (dict): Parameters specific to this experiment.
            config (ExperimentConfig): Configuration specific to this experiment.
        """
        # Create a timestamped experiment directory
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        experiment_name =  f'{config.experiment_name}_{hashlib.md5(timestamp.encode()).hexdigest()}'
        experiment_path = os.path.join(self.experiment_dir, experiment_name)
        os.makedirs(experiment_path)

        # Log parameters to a JSON file
        parameters_path = os.path.join(experiment_path, 'parameters.json')
        with open(parameters_path, 'w') as param_file:
            json.dump(parameters, param_file, indent=4)

        # Create a function to run the experiment with a timeout
        def run_experiment_with_timeout():
            nonlocal experiment_output
            try:
                experiment_output = experiment_fn(parameters)
            except Exception as e:
                experiment_output = {'error': str(e)}

        # Run the experiment in a separate process
        experiment_output = None
        process = multiprocessing.Process(target=run_experiment_with_timeout)
        process.start()

        # Wait for the process to finish or timeout
        process.join(config.max_duration_seconds)

        # Terminate the process if it's still running after the timeout
        if process.is_alive():
            process.terminate()
            process.join()

            # Log timeout information
            timeout_info = {'timeout_seconds': config.max_duration_seconds}
            experiment_output = {'error': 'Experiment timed out', 'timeout_info': timeout_info}

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
    experiment_parameters = {'param1': 42, 'param2': 'abc'}
    experiment_config = ExperimentConfig(max_duration_seconds=3600, experiment_name='my_experiment')
    # Example experiment function
    def my_experiment(config: Dict[str, Any] = None):
        # Your experiment code here
        print(f"Running experiment with config: {config}")
        time.sleep(10)  # Simulate a long-running experiment
        return {'result': 'some_data'}

    # Example usage
    harness = ExperimentHarness(experiment_dir='my_experiments')
    harness.run_experiment(my_experiment, experiment_parameters, config=experiment_config)
