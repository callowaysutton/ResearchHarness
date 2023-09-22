import os
import json
import csv
import datetime
import hashlib
from typing import Dict, Any
import multiprocessing
import time

class ExperimentConfig:
    def __init__(self, max_duration_seconds: int = 10, experiment_name: str = "experiment", experiment_repetitions: int = 1, experiment_repetition_delay: int = 0):
        """
        Initialize the ExperimentConfig.

        Args:
            max_duration_seconds (int): Maximum time (in seconds) the experiment is allowed to run.
            experiment_name (str): Name of the experiment.
            experiment_repetitions (int): Number of times to repeat the experiment.
            experiment_repetition_delay (int): Delay (in seconds) between experiment repetitions.
        """
        self.max_duration_seconds = max_duration_seconds
        self.experiment_name = experiment_name
        self.experiment_repetitions = experiment_repetitions
        self.experiment_repetition_delay = experiment_repetition_delay
        

class ExperimentHarness:
    def __init__(self, experiment_dir: str = 'experiments', config: ExperimentConfig = None):
        """
        Initialize the ExperimentHarness.

        Args:
            experiment_dir (str): Directory to store experiment logs and results.
        """
        self.experiment_dir = experiment_dir
        os.makedirs(experiment_dir, exist_ok=True)
        
        if config is None:
            print("No config provided, using default config")
            self.config = ExperimentConfig()
        else:
            self.config = config

    def run_experiment(self, experiment_fn: callable = (), parameters: Dict[str, Any] = None):
        """
        Run an experiment and log the results.

        Args:
            experiment_fn (callable): The experiment function to run.
            parameters (dict): Parameters specific to this experiment.
            config (ExperimentConfig): Configuration specific to this experiment.
        """
        
        if self.config.experiment_repetitions < 0 or self.config is None:
            print("Invalid amount of repititions in config")
            return
        
        if self.config.experiment_repetition_delay < 0 or self.config is None:
            print("Invalid repitition delay in config")
            return
        
        for _ in range(self.config.experiment_repetitions):
            # Create a timestamped experiment directory
            start_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
            experiment_name =  f'{self.config.experiment_name}_{start_timestamp}'
            experiment_path = os.path.join(self.experiment_dir, experiment_name)
            os.makedirs(experiment_path)

            # Log parameters to a JSON file
            parameters_path = os.path.join(experiment_path, 'parameters.json')
            with open(parameters_path, 'w') as param_file:
                json.dump(parameters, param_file, indent=4)

            # Create a function to run the experiment with a timeout
            def run_experiment_with_timeout(experiment_path: str):
                nonlocal experiment_output
                try:
                    # Log experiment output to a JSON file
                    experiment_output = experiment_fn(parameters)
                    output_path = os.path.join(experiment_path, 'output.json')
                    with open(output_path, 'w') as output_file:
                        json.dump(experiment_output, output_file, indent=4)
                except Exception as e:
                    experiment_output = {'error': str(e)}

            # Run the experiment in a separate process
            experiment_output = None
            process = multiprocessing.Process(target=run_experiment_with_timeout, args=(experiment_path,))
            output_path = os.path.join(experiment_path, 'output.json')
            process.start()

            # Wait for the process to finish or timeout
            process.join(self.config.max_duration_seconds)
            
            end_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")

            # Terminate the process if it's still running after the timeout
            if process.is_alive():
                process.terminate()
                process.join()

                # Log timeout information
                timeout_info = {'timeout_seconds': self.config.max_duration_seconds}
                experiment_output = {'error': 'Experiment timed out', 'timeout_info': timeout_info}            

            # Log experiment information to a CSV file
            csv_path = os.path.join(self.experiment_dir, 'experiments.csv')
            experiment_info = {
                'experiment_name': experiment_name,
                'start_time': start_timestamp,
                'end_time': end_timestamp,
                'parameters_path': parameters_path,
                'output_path': output_path,
            }

            # Append experiment information to the CSV file
            with open(csv_path, 'a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=experiment_info.keys())
                if os.stat(csv_path).st_size == 0:
                    writer.writeheader()
                writer.writerow(experiment_info)
            time.sleep(self.config.experiment_repetition_delay)

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
    harness = ExperimentHarness(experiment_dir='my_experiments', config=experiment_config)
    harness.run_experiment(my_experiment, parameters=experiment_parameters)