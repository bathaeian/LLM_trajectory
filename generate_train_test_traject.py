import argparse
import json
import re

def split_trajectories(input_file, train_file, test_file):
    """
    Reads a JSON file with trajectories and splits into train/test sets
    based on the parity of the numeric suffix in the name.
    Odd numbers (T1, T3, ...) -> train
    Even numbers (T2, T4, ...) -> test
    """
    with open(input_file, 'r') as f:
        data = json.load(f)

    train_lines = []
    test_lines = []

    for entry in data:
        name = entry["name"]          # e.g., "T1"
        trajectory = entry["trajectory"]
        # Extract the number after 'T'
        num = int(re.search(r'\d+', name).group())
        line = f"{name}={trajectory}"

        if num % 2 == 1:              # odd → train
            train_lines.append(line)
        else:                         # even → test
            test_lines.append(line)

    # Write train file
    with open(train_file, 'w') as f:
        f.write("\n".join(train_lines))

    # Write test file
    with open(test_file, 'w') as f:
        f.write("\n".join(test_lines))

    print(f"Train lines: {len(train_lines)}")
    print(f"Test lines:  {len(test_lines)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Encoding of trajectories."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the hamiltonian dataset file.",
    )

    parser.add_argument(
        "--outtrain",
        required=True,
        help="path to the train trajectory file.",
    )

    parser.add_argument(
        "--outtest",
        required=True,
        help="path to the test trajectory file.",
    )
    args = parser.parse_args()
    data_file = args.input
    train_file = args.outtrain
    test_file = args.outtest
    split_trajectories(data_file, train_file, test_file)