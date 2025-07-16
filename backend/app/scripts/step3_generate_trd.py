import os
import sys
import anthropic # Import for direct API interaction
from load_dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

def generate_trd():
    """
    Generates a Technical Requirements Document (TRD) from an existing
    Product Requirements Document (PRD) using the Anthropic Claude API,
    streaming the output to a file.
    """
    prd_file = "./docs/PRD.md" # Source PRD file
    trd_output_file = "./docs/TRD.md" # Output TRD file

    print("Starting TRD generation process...")

    # --- Step 1: Initialize Anthropic Client ---
    try:
        # Explicitly pass api_key as an empty string to allow the Canvas environment to inject it.
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    except Exception as e:
        print(f"Error initializing Anthropic client: {e}", file=sys.stderr)
        print("Please ensure the Anthropic library is correctly installed and configured.", file=sys.stderr)
        sys.exit(1)

    # --- Step 2: Check for PRD file existence ---
    if not os.path.exists(prd_file):
        print(f"Error: Product Requirements Document (PRD) file not found at '{prd_file}'.", file=sys.stderr)
        print("Please ensure the 'docs' directory exists in your current project and 'PRD.md' is inside it.", file=sys.stderr)
        sys.exit(1)

    print(f"Reading PRD content from '{prd_file}'...")
    try:
        with open(prd_file, 'r') as f:
            prd_content = f.read()
    except IOError as e:
        print(f"Error reading PRD file '{prd_file}': {e}", file=sys.stderr)
        sys.exit(1)

    # --- Step 3: Generate TRD.md (Technical Requirements Document) ---
    print(f"Generating '{trd_output_file}'...")

    # Create docs directory if it doesn't exist
    os.makedirs(os.path.dirname(trd_output_file), exist_ok=True)

    # Prompt for the TRD, focusing on translating product needs into technical requirements
    # Using an f-string to embed the PRD content
    trd_prompt = f"""Based on the following Product Requirements Document (PRD), generate a detailed Technical Requirements Document (TRD).
This TRD should translate the functional and non-functional requirements from the PRD into a detailed technical specification.
Include the following sections:
1.  **System Architecture:** Describe the chosen architecture (e.g., three-tier).
2.  **Frontend (Client-Side):** Specify framework, language, state management, routing, styling, API communication, and build tool.
3.  **Backend (Server-Side):** Specify framework, language, authentication mechanism, database communication, and a high-level API specification.
4.  **Database:** Specify the database system mentioned in the PRD and provide data models for the main entities (Users, Tasks) with fields, types, and relationships.
5.  **Deployment and Infrastructure:** Describe containerization strategy, hosting provider options, and CI/CD.
6.  **Non-Functional Requirements:** Detail how performance, security, scalability, and accessibility requirements from the PRD will be technically addressed.

Focus on translating product needs into concrete technical requirements and constraints.

--- Start of PRD Content ---
{prd_content}
--- End of PRD Content ---"""

    # Call Claude API to generate content and stream output to the TRD file
    try:
        with open(trd_output_file, 'w') as f_out:
            with client.messages.stream(
                model="claude-opus-4-20250514", # Using the model from your example
                max_tokens=4000, # Adjusted for a comprehensive TRD document
                temperature=0.7, # A slightly lower temperature for more focused technical output
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": trd_prompt
                            }
                        ]
                    }
                ]
            ) as stream:
                for chunk in stream:
                    if chunk.type == "content_block_delta":
                        if chunk.delta.type == "text_delta":
                            text_content = chunk.delta.text
                            f_out.write(text_content)
                            # Optional: print to console as well to show real-time progress
                            sys.stdout.write(text_content)
                            sys.stdout.flush() # Ensure the output is immediately visible
        print(f"\nSuccessfully generated '{trd_output_file}'.") # Newline after streaming output

    except anthropic.APIError as e:
        print(f"Error calling Claude API: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    print("TRD generation complete.")
    print(f"You can find the generated document at: '{trd_output_file}'")
    print("Please review the generated content, as AI-generated documents may require human refinement.")

# This ensures that generate_trd() is called only when the script is executed directly
if __name__ == "__main__":
    generate_trd()
