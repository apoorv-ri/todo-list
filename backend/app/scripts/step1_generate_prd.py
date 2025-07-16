import os
import sys
import anthropic # New import for direct API interaction
from load_dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

def generate_prd2():
    """
    Generates a Product Requirements Document (PRD2) using the Anthropic Claude API,
    taking project details as input and streaming the output to a file.
    """
    prd2_output_file = "./docs/PRD2.md"

    print("Starting PRD2 generation process...")

    # --- Step 1: Initialize Anthropic Client ---
    # The Anthropic API key is typically loaded from an environment variable or configuration.
    # For this environment, it's handled automatically.
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    except Exception as e:
        print(f"Error initializing Anthropic client: {e}", file=sys.stderr)
        print("Please ensure the Anthropic library is correctly installed and configured.", file=sys.stderr)
        sys.exit(1)

    # --- Step 2: Get user input for project name and description ---
    print("Please provide the following information to generate your PRD2:")
    project_name = input("Project Name: ").strip()
    project_description = input("Short Description: ").strip()

    # Validate inputs
    if not project_name:
        print("Error: Project name cannot be empty.", file=sys.stderr)
        sys.exit(1)
    if not project_description:
        print("Error: Project description cannot be empty.", file=sys.stderr)
        sys.exit(1)

    print(f"Generating PRD2 for project: {project_name}")

    # --- Step 3: Generate PRD2.md ---
    print(f"Generating '{prd2_output_file}'...")

    # Create docs directory if it doesn't exist
    # os.makedirs creates directories recursively; exist_ok=True prevents error if it already exists
    os.makedirs(os.path.dirname(prd2_output_file), exist_ok=True)

    # Prompt for the PRD2 generation - comprehensive PRD content
    # Using an f-string for easy variable interpolation
    prd2_prompt = f"""Create a comprehensive Product Requirements Document for {project_name} - {project_description}

Include:
- Executive summary with objectives
- Problem statement and target users
- Solution overview with key features
- Functional requirements with user stories
- Non-functional requirements
- Technical constraints
- Success criteria
- Timeline and risks

Generate detailed content for each section."""

    # Call Claude API to generate content and stream output to the PRD2 file
    try:
        # Open the output file in write mode ('w')
        with open(prd2_output_file, 'w') as f_out:
            # Use client.messages.stream for streaming output, as requested.
            # max_tokens is set to a reasonable value for a document like a PRD.
            with client.messages.stream(
                model="claude-opus-4-20250514", # Model specified in your example
                max_tokens=4000, # Adjusted for a comprehensive PRD document
                temperature=1, # Temperature specified in your example
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prd2_prompt
                            }
                        ]
                    }
                ]
            ) as stream:
                # Iterate over chunks from the stream and write to file
                for chunk in stream:
                    if chunk.type == "content_block_delta":
                        if chunk.delta.type == "text_delta":
                            text_content = chunk.delta.text
                            f_out.write(text_content)
                            # Optional: print to console as well to show real-time progress
                            sys.stdout.write(text_content)
                            sys.stdout.flush() # Ensure the output is immediately visible
        print(f"\nSuccessfully generated '{prd2_output_file}'.") # Newline after streaming output

    except anthropic.APIError as e:
        # Catch specific API errors from Anthropic
        print(f"Error calling Claude API: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    print("PRD2 generation complete.")
    print(f"You can find the generated document at: '{prd2_output_file}'")
    print("Please review the generated content, as AI-generated documents may require human refinement.")

# This ensures that generate_prd2() is called only when the script is executed directly
if __name__ == "__main__":
    generate_prd2()
