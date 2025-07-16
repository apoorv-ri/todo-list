import os
import sys
import anthropic # Import for direct API interaction
from load_dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

def generate_tsd():
    """
    Generates a Technical Requirements Document (TSD) from an existing
    Product Requirements Document (PRD) using the Anthropic Claude API,
    streaming the output to a file.
    """
    prd_file = "./docs/PRD.md" # Source PRD file
    tsd_output_file = "./docs/TSD.md" # Output TSD file

    print("Starting TSD generation process...")

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

    # --- Step 3: Generate TSD.md (Technical Requirements Document) ---
    print(f"Generating '{tsd_output_file}'...")

    # Create docs directory if it doesn't exist
    os.makedirs(os.path.dirname(tsd_output_file), exist_ok=True)

    # Prompt for the TSD, focusing on translating product needs into technical requirements
    # Using an f-string to embed the PRD content
    tsd_prompt = f"""Based on the following Product Requirements Document (PRD), generate a detailed Technical System Design (TSD).
This TSD should outline the 'how' of implementing the product.
Include the following sections with technical details:
1.  **System Architecture Diagram:** A simple text-based diagram showing Frontend, Backend, and Database interaction.
2.  **Component Design:** Break down the frontend and backend into logical components/modules.
3.  **API Endpoint Design:** List the specific RESTful API endpoints, including HTTP methods and paths.
4.  **Database Schema Design:** Visually represent the database tables/collections and their relationships.
5.  **Data Flow Examples:** Describe the step-by-step data flow for 2-3 key user actions (e.g., User Login, Create Task).
6.  **Security Design:** Briefly describe the design for authentication (JWT flow) and authorization.

Focus on the high-level design, component interactions, and data flows.
Show sequence daiagrams or flowcharts where appropriate in ASCIIflow diagram format.

--- Start of PRD Content ---
{prd_content}
--- End of PRD Content ---"""

    # Call Claude API to generate content and stream output to the TSD file
    try:
        with open(tsd_output_file, 'w') as f_out:
            with client.messages.stream(
                model="claude-opus-4-20250514", # Using the model from your example
                max_tokens=4000, # Adjusted for a comprehensive TSD document
                temperature=0.7, # A slightly lower temperature for more focused technical output
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": tsd_prompt
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
        print(f"\nSuccessfully generated '{tsd_output_file}'.") # Newline after streaming output

    except anthropic.APIError as e:
        print(f"Error calling Claude API: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    print("TSD generation complete.")
    print(f"You can find the generated document at: '{tsd_output_file}'")
    print("Please review the generated content, as AI-generated documents may require human refinement.")

# This ensures that generate_tsd() is called only when the script is executed directly
if __name__ == "__main__":
    generate_tsd()
