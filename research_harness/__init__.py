# research_harness/__init__.py
# Put some helper functions here as need be :)
import subprocess
from typing import Dict, Any

def run_shell_command(config: Dict[str, Any] = None):
    """
    Run a shell command in a separate process and capture stdout, stderr, etc.

    Args:
        command (str): The shell command to run.

    Returns:
        dict: A dictionary containing the following keys:
            - 'stdout': Captured stdout as a string.
            - 'stderr': Captured stderr as a string.
            - 'returncode': The return code of the command.
    """
    
    print(f"Running shell experiment with the config: {config}")
    
    try:
        result = subprocess.run(
            config["command"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,  # Capture output as strings
        )
        
        # Create a dictionary to store the results
        output_dict = {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
        }
        
        return output_dict

    except Exception as e:
        # Handle exceptions if the command execution fails
        return {'error': str(e)}
    
if __name__ == "__main__":
    from research_harness import ExperimentHarness
    from research_harness import ExperimentConfig

    experiment_parameters = {'command': ["htop"]}  # Customize as needed
    # Example usage
    harness = ExperimentHarness(experiment_dir='my_experiments')
    experiment_config = ExperimentConfig(max_duration_seconds=1, experiment_name='my_experiment')
    harness.run_experiment(run_shell_command, parameters = experiment_parameters, config = experiment_config)
else:
    from .research_harness import ExperimentHarness
    __all__ = [ExperimentHarness]