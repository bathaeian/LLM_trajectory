import argparse
import json
def generate_trajectories(input_file, output_file):
    """Read trajectories from input_file and write move sequences to output_file."""
    
    # Direction mapping: (dx, dy) -> symbol
    direction_map = {
        (0, -1): 'N',
        (0, 1): 'S',
        (1, 0): 'E',
        (-1, 0): 'W',
        (-1, -1): 'WN',
        (1, -1): 'NE',
        (1, 1): 'ES',
        (-1, 1): 'SW',
        (0, -2): 'N',
        (0, 2): 'S',
        (2, 0): 'E',
        (-2, 0): 'W',
        (-2, -1): 'WN',
        (2, -1): 'NE',
        (2, 1): 'ES',
        (-2, 1): 'SW',
        (-1, -2): 'WN',
        (1, -2): 'NE',
        (1, 2): 'ES',
        (-1, 2): 'SW',
        (-2, -2): 'WN',
        (2, -2): 'NE',
        (2, 2): 'ES',
        (-2, 2): 'SW',
    }
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    results = []
    for entry in data:
        name = entry['name']
        path = entry['path']
        moves = []
        
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            dx = x2 - x1
            dy = y2 - y1
            move = direction_map.get((dx, dy))
            if move is None:
                # Fallback for unexpected steps (should not happen)
                move = f"({dx},{dy})"
            moves.append(move)
        trajectory_str = ''.join(moves)
        results.append({
            "name": name,
            "trajectory": trajectory_str
        })
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Trajectories written to {output_file}")

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
        "--output",
        required=True,
        help="path to the trajectory file.",
    )
    args = parser.parse_args()
    data_file = args.input
    hamilton_file = args.output
    generate_trajectories(data_file, hamilton_file)