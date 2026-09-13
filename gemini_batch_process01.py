"""
Read a file line by line, send each line to Google Gemini, and save the results.

Setup:
    pip install google-generativeai

    Get an API key from https://aistudio.google.com/app/apikey
    Then either:
      - set it as an environment variable:  export GEMINI_API_KEY="your-key-here"
      - or paste it directly into API_KEY below (not recommended for shared code)

Usage:
    python gemini_batch_process01.py input.txt output.txt
"""

import os
import sys
import time
import google.generativeai as genai

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_KEY = os.environ.get("GEMINI_API_KEY", "")  # or hardcode your key here as a string
MODEL_NAME = "gemini-3.6-flash"                  # change to another Gemini model if you prefer
DELAY_BETWEEN_REQUESTS = 1.0                     # seconds, to avoid hitting rate limits
PROMPT_TEMPLATE = """You are an intelligent pattern analyzer. We have 10 classes of trajectories.
class1= a spiral that repeatedly changes its direction like right->down->left->up->...
class2= a well-like trajectory that sequence of its movement is like deep down->right->high up or  deep down->left->high up
class3= a hook-like trajectory. The first part of its trajectory is a long vertical line. The second part is a small hook and the third part moves east and south in a zigzag way.
class4= horizontally mirrored blocky 9 with a long irregular zigzag tail. The first part of its trajectory makes a square. The second part goes zigzaggy to the deep down and the third part redirects to the right.
class5=a blocky pot with handles. Its trajectory can be described in 5 parts. The first and the fifth part are zigzaggy movements that form the handles. The second and the forth parts are vertical and the third or middle part is a very very long horizontal line.
class6= a 2-like trajectory. Its sequence of movement is up->right->down->very long left->small down->very long rigth
class7= upper case J-like trajectory with a horizontal long top cover. The first part of its trajectory begins with long horizontal line to right and the second part begins with going to deep down and continues zigzaggy to left.
class8= blocky 6. its trajectory begins with long left, then goes to the deep  and at the end makes a square. The square may have the trajectory of down->right->up->left or right->down->left->up
class9= rounded irregular curve that bends to the right and comes back to the left. The first part of its trajectory begins with zigzag movement to the west and sout and then backs to the east. The second part which is longer than first part begins with movement to wast and south and continues its zigzaggy movement to the west.
class10= Greek small Pi-like trajectory. it begins with a vertical path, the middle part is a long horizontal path with a zigzag in the middle. The trajectory ends with a very very long vertical line.
Given the following TRAJECTORY:
VARIABLE_DECLARATION: TRAJECTORY_VAR={trajectory}
determine the class of it based on classes 1 to 10.  """                      


def get_model():
    if not API_KEY:
        raise RuntimeError(
            "No API key found. Set the GEMINI_API_KEY environment variable "
            "or edit API_KEY in this script."
        )
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(MODEL_NAME)


def process_file(input_path: str, output_path: str):
    model = get_model()

    with open(input_path, "r", encoding="utf-8") as infile:
        lines = [line.rstrip("\n") for line in infile]

    results = []
    total = len(lines)

    with open(output_path, "w", encoding="utf-8") as outfile:
        for i, line in enumerate(lines, start=1):
            if not line.strip():
                # skip empty lines but keep numbering/output consistent
                outfile.write("\n")
                continue

            prompt = PROMPT_TEMPLATE.format(trajectory=line)
            print(f"[{i}/{total}] Sending: {line[:60]!r}")

            try:
                response = model.generate_content(prompt)
                answer = response.text.strip() if response.text else ""
            except Exception as e:
                answer = f"[ERROR: {e}]"

            outfile.write(answer + "\n")
            outfile.flush()  # save progress as we go, in case of interruption
            results.append(answer)

            time.sleep(DELAY_BETWEEN_REQUESTS)

    print(f"\nDone. Results saved to: {output_path}")
    return results


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gemini_batch_process.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_file(input_file, output_file)
