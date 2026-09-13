from typing import Hashable
import os
import argparse
import json
import ast
import math

Node = tuple[int, int]  
Graph = dict[Node, set[Node]]
max_gap=0
def prune_intersecting_paths(longest_paths: dict[Node, list[Node]]) -> dict[Node, list[Node]]:
    """
    Remove shorter paths when two paths intersect.
    Keeps the longest possible set of mutually non‑intersecting paths.
    """
    if not longest_paths:
        return {}

    # Sort items by length descending (longest first)
    sorted_items = sorted(longest_paths.items(), key=lambda kv: len(kv[1]), reverse=True)

    kept_paths: dict[Node, list[Node]] = {}
    kept_sets: list[set[Node]] = []

    for node, path in sorted_items:
        path_set = set(path)
        # Check if this path intersects any already‑kept path
        intersects = any(path_set & kept_set for kept_set in kept_sets)
        if not intersects:
            kept_paths[node] = path
            kept_sets.append(path_set)

    return kept_paths
def parse_points(points_str):
    """Convert a string like '((10, 6), (12, 6), ...)' into a list of tuples."""
    # Use ast.literal_eval to safely parse the Python literal
    points_tuple = ast.literal_eval(points_str)
    # It might be a tuple of tuples; convert to list for consistent formatting
    return list(points_tuple)

def build_point_cloud_graph(points: list[Node]) -> Graph:
    """
    Build a graph from a point cloud.

    Two points are connected if they are at most one grid step
    apart in both coordinates, excluding the point itself.

    This includes the four cardinal and four diagonal directions.
    """
    graph: Graph = {point: set() for point in points}
    for point in points:
        x, y = point
        for other in points:
            if point == other:
                continue

            other_x, other_y = other

            if (
                abs(x - other_x) <= 1
                and abs(y - other_y) <= 1
            ):
                graph[point].add(other)
    return graph
def diff(a: Node, b: Node) -> int:
    # If a and b are tuples of two ints, this works.
    # If they're something else, handle it.
    if isinstance(a, tuple) and len(a) >= 2 and isinstance(b, tuple) and len(b) >= 2:
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    # Fallback: maybe nodes are numbers or other comparable objects
    return abs(a - b) if isinstance(a, (int, float)) else 0
def merge_path(l:list[Node],sl:list[Node]) ->[list[Node], Bool]:
    if sl is None:
        return l, False
    l = list(l) if not isinstance(l, list) else l
    sl = list(sl) if not isinstance(sl, list) else sl
    if (
        diff(l[0], sl[0]) <=max_gap
        ):
        l.reverse()
        return l+sl,True
    if (
        diff(l[0] ,sl[-1]) <= max_gap
    ):
        return sl+l,True
    if (
        diff(l[-1] , sl[-1]) <= max_gap
    ):
        sl.reverse()
        return l+sl,True
    if (
        diff(l[-1], sl[0]) <= max_gap
    ):
        return l+sl,True
    return l,False

def find_longest_simple_path(graph: Graph) -> list[Node]:
    """
    Find the longest simple path in the graph.

    A simple path visits each vertex at most once.
    Unlike a Hamiltonian path, it does not have to visit
    every vertex in the graph.

    Args:
        graph: An adjacency-list representation of the graph.

    Returns:
        A longest simple path. If the graph is empty, returns [].
    """
    if not graph:
        return []

    nodes = list(graph)
    longest_path: list[Node] = []
    longest_paths:dict[Node,list[Node]]={}

    def dfs(
        node: Node,
        path: list[Node],
        visited: set[Node],
    ) -> None:
        for neighbor in graph[node]:
            if neighbor in visited:
                continue

            visited.add(neighbor)
            path.append(neighbor)

            dfs(neighbor, path, visited)
            if len(path) > len(longest_paths.get(neighbor,[])):
                longest_paths[neighbor] = path.copy()
            path.pop()
            visited.remove(neighbor)
    for start in list(set(nodes)-set(longest_paths)):
        dfs(start, [start], {start})
        print("*********************")
    longest_paths = prune_intersecting_paths(longest_paths)
    print("^^^^^^^^^")   
    sorted_longest_paths = sorted(longest_paths.items(), key=lambda item: len(item[1]), reverse=True)
    # Filter out paths with length <= 2
    filtered_paths = [(node, path) for node, path in sorted_longest_paths if len(path) > 2]
    merged = filtered_paths[0] if filtered_paths else None      
    print("$$$$$$$$$$")
    merged_path= merged[1] if merged else []
    unmerged_paths = [path for _, path in filtered_paths[1:]]
    failed_attempts = 0
    max_failures = len(unmerged_paths) + 1  # safety threshold

    while unmerged_paths and failed_attempts < max_failures:
        other = unmerged_paths.pop(0)              
        new_path, merged_flag = merge_path(merged_path, other)

        if merged_flag:
            # Successful merge – discard 'other', update merged
            merged_path = new_path.copy()
            failed_attempts = 0  # reset on success
            # Continue; we don't put 'other' back because it's consumed
        else:
            # No merge – put 'other' at the end to try again later
            unmerged_paths.append(other)
            failed_attempts += 1

    #merged= list(merged) if not isinstance(merged, list) else merged
    if (merged_path[0][1])>(merged_path[-1][1]):
        merged_path.reverse()
    return merged_path

def main():
    parser = argparse.ArgumentParser(
        description="Convert point clouds to trajectories."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the train dataset directory.",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="path to the hamilton file.",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help="prefix of the file name. "
    )
    args = parser.parse_args()
    data_folder = args.input
    hamilton_file = args.output
    prefix=args.prefix
    all_hamilton=[]
    for i in range(1, 21):
        json_filename = f"{prefix}{i}.json"
        data_full_path = os.path.join(data_folder, json_filename)
        if not os.path.exists(data_full_path):
            print(f"Warning: {data_full_path} not found, skipping.")
            continue

        try:
            with open(data_full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {data_full_path}: {e}")
            continue
        points_str = data.get("points")
        max_gap= math.ceil(math.sqrt(data.get("num_points"))/3)
        if points_str is None:
            print(f"Warning: 'points' field missing in {data_full_path}, skipping.")
            continue

        try:
            points = parse_points(points_str)
        except Exception as e:
            print(f"Error parsing points in {data_full_path}: {e}")
            continue
        # Generate the new simple path
        graph = build_point_cloud_graph(points)

        path = find_longest_simple_path(graph)
        hamilton={
            "name":f"T{i}",
            "path": path
        }
        all_hamilton.append(hamilton)
        # Write the output file
    try:
        with open(hamilton_file, "w", encoding="utf-8") as f:
            json.dump(all_hamilton, f, indent=4, ensure_ascii=False) 
    except Exception as e:
        print(f"Error writing {hamilton_file}: {e}")

if __name__ == "__main__":
    main()