import os
import shutil
import subprocess
import sys
from load_dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

def generate_tasks():
    """
    Generates a list of development tasks and sub-tasks from PRD, TRD, and TSD
    documents using a hypothetical 'task-master' CLI tool.
    """
    # --- Define File Paths ---
    # IMPORTANT: Please ensure these files exist in the specified paths.
    prd_file = "./docs/PRD.md" # Assuming PRD stands for Project/Product Requirements Document
    trd_file = "./docs/TRD.md"
    tsd_file = "./docs/TSD.md"
    tasks_output_file = "./docs/generated_tasks.md"
    temp_input_file = "./.taskmaster_temp_input.txt" # Temporary file for combined input

    # Define the team roles for task assignment
    TEAM_ROLES="""
1. Backend Developer
2. Frontend Developer
3. DevOps Developer
4. Blockchain Developer
"""

    print("--- Starting Task Generation Process ---")

    # --- Step 1: Check for task-master CLI ---
    task_master_cli_path = shutil.which("task-master")
    if not task_master_cli_path:
        print("Error: 'task-master' CLI not found.", file=sys.stderr)
        print("Please ensure the task-master.dev CLI is installed and configured in your PATH.", file=sys.stderr)
        print("Refer to task-master.dev documentation for installation instructions.", file=sys.stderr)
        sys.exit(1)

    # --- Step 2: Check for input document existence ---
    required_files = [prd_file, trd_file, tsd_file]
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"Error: Required document file not found at '{file_path}'.", file=sys.stderr)
            print("Please ensure the 'docs' directory exists in your current project and all required documents are inside it.", file=sys.stderr)
            sys.exit(1)

    print(f"Reading document content from '{prd_file}', '{trd_file}', and '{tsd_file}'...")

    # Read the entire content of the documents into variables
    try:
        with open(prd_file, 'r') as f:
            prd_content = f.read()
        with open(trd_file, 'r') as f:
            trd_content = f.read()
        with open(tsd_file, 'r') as f:
            tsd_content = f.read()
    except IOError as e:
        print(f"Error reading input files: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Step 3: Run task-master init (if necessary) ---
    # The bash script includes 'task-master init'.
    # This might be for initializing a project or configuration.
    # We'll run it, but note that its necessity depends on the actual CLI.
    # print("Running 'task-master init'...")
    # try:
    #     init_process = subprocess.run(
    #         [task_master_cli_path, "init"],
    #         capture_output=True,
    #         text=True,
    #         check=False # Do not raise an exception for non-zero exit codes yet
    #     )
    #     if init_process.returncode == 0:
    #         print("task-master init completed successfully.")
    #     else:
    #         print(f"Warning: 'task-master init' failed or returned non-zero exit code {init_process.returncode}.", file=sys.stderr)
    #         print(f"Stdout: {init_process.stdout}", file=sys.stderr)
    #         print(f"Stderr: {init_process.stderr}", file=sys.stderr)
    #         # Decide if you want to exit here or continue. For now, it's a warning.

    # except Exception as e:
    #     print(f"An error occurred during 'task-master init': {e}", file=sys.stderr)
        # Decide if you want to exit here or continue. For now, it's a warning.


    # --- Step 4: Prepare combined input for task-master CLI ---
    print(f"Preparing combined input for task-master CLI in '{temp_input_file}'...")

    # Construct the prompt for task-master.dev CLI
    # This prompt guides the AI on how to break down tasks and assign them.
    # The content of PRD, TRD, TSD is appended to this prompt.
    task_prompt = f"""
Generate a detailed list of development tasks and sub-tasks based on the following Project/Product Requirements Document (PRD), Technical Requirements Document (TRD), and Technical System Design (TSD).

For each task, clearly define:
-   **Task Name:** A concise description of the task.
-   **Description:** A brief explanation of what needs to be done.
-   **Assigned To:** Assign to one of the following team roles:
    {TEAM_ROLES.strip()}
-   **Dependencies:** List any tasks that must be completed before this one.
-   **Estimated Effort:** Provide a rough estimate (e.g., Small, Medium, Large, or hours/days if possible).

Break down larger tasks into logical sub-tasks. Ensure all aspects mentioned in the documents are covered. Prioritize tasks where possible.

--- Start of PRD Content ---
{prd_content}
--- End of PRD Content ---

--- Start of TRD Content ---
{trd_content}
--- End of TRD Content ---

--- Start of TSD Content ---
{tsd_content}
--- End of TSD Content ---
"""

    # Write the combined prompt and document content to a temporary file
    try:
        with open(temp_input_file, 'w') as f_temp:
            f_temp.write(task_prompt)
    except IOError as e:
        print(f"Error writing temporary input file '{temp_input_file}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- Step 5: Generate Tasks and Sub-tasks using task-master CLI (parse-prd) ---
    print(f"Generating tasks and sub-tasks using '{task_master_cli_path} parse-prd'...")

    # Create the 'tasks' directory if it doesn't exist
    os.makedirs(os.path.dirname(tasks_output_file), exist_ok=True)

    try:
        # subprocess.Popen is used for running external commands and streaming output.
        process = subprocess.Popen(
            [task_master_cli_path, "parse-prd", temp_input_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1 # Line-buffered output for streaming
        )

        # Stream output to file
        with open(tasks_output_file, 'w') as f_out:
            for line in process.stdout:
                f_out.write(line)
                # Optional: print to console as well to show real-time progress
                sys.stdout.write(line)
                sys.stdout.flush() # Ensure the output is immediately visible

        # Wait for the subprocess to complete and get its return code
        process.wait()

        # Check the return code of the subprocess
        if process.returncode == 0:
            print(f"\nSuccessfully generated tasks to '{tasks_output_file}'.")
        else:
            stderr_output = process.stderr.read()
            print(f"Error: Failed to generate tasks to '{tasks_output_file}'.", file=sys.stderr)
            if stderr_output:
                print(f"task-master CLI Error Output:\n{stderr_output}", file=sys.stderr)
            sys.exit(1)

    except FileNotFoundError:
        print(f"Error: The 'task-master' command was not found. Please ensure it's installed and in your PATH.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred during task generation: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        # --- Step 6: Clean up temporary file ---
        if os.path.exists(temp_input_file):
            print(f"Cleaning up temporary input file '{temp_input_file}'...")
            os.remove(temp_input_file)

    print("Task generation complete.")
    print(f"Please review the generated tasks at: '{tasks_output_file}'")
    print("AI-generated tasks may require human refinement and detailed planning.")

# This ensures that generate_tasks() is called only when the script is executed directly
if __name__ == "__main__":
    generate_tasks()
