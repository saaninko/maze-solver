"""Maze Solver

This wee program solves a maze in a file given by the user as a command line argument.
The file should be in .txt format and the structure of the maze follows the following rules:
    * Character `#` represents a block in the maze
    * Whitespace character represents movable space
    * Character `E` represents an exit point
    * The edges of the maze can only contain exit or entry points (in addition to `#`)
      and there should not be any extra characters outside of the maze

The mazer can move up, down, left and right where there is movable space. Each move
has an equal cost.
"""
import argparse
import os
import sys
from queue import PriorityQueue

SPACE = " "
START = "^"
EXIT = "E"


class MazeParseError(Exception):
    """Indicates an error in the format of the maze."""


class NotSolvableError(Exception):
    """Indicates that the maze is not solvable."""


def _is_on_grid(maze_map: list, point: tuple) -> bool:
    row, col = point
    return (
        0 <= row < len(maze_map)
        and 0 <= col < len(maze_map[0])
        and maze_map[row][col] in (EXIT, SPACE)
    )


def _get_neighbors(maze_map: list, point: tuple) -> list:
    """Get neighbor points for `point`. Discard points that can't be traveled through."""
    row, col = point
    return [
        n_point
        for n_point in [
            (row + 1, col),
            (row - 1, col),
            (row, col + 1),
            (row, col - 1),
        ]
        if _is_on_grid(maze_map, n_point)
    ]


def _trace_path_from_exit(
    neighbors: dict, exit_point: tuple, starting_point: tuple
) -> dict:
    """Trace the path from `exit_point` in `paths` to find the shortest
    route to `starting_point`.
    """
    backwards_path = {}
    # If exit point was reached, follow the path from exit point to starting point
    if exit_point in neighbors:
        backwards_path[exit_point] = None
        cell = exit_point
        while cell != starting_point:
            backwards_path[neighbors[cell]] = cell
            cell = neighbors[cell]
    return backwards_path


def _get_path_cost(start: tuple, destination: tuple) -> int:
    """Calculate the cost to travel from point `start` to `destination`
    using the Manhattan distance.
    """
    row_start, col_start = start
    row_dest, col_dest = destination
    return abs(row_start - row_dest) + abs(col_start - col_dest)


def _get_path(maze_map: list, starting_point: tuple, exit_point: tuple) -> dict:
    """Calculate the cheapest path from `starting_point` to
    `exit_point` using the A* algorithm.

    :return: A mapping of the path. Each key is a tuple (point)
    and its value is the point's predecessor.
    """
    # Costs from starting point to  point (key).
    g_score = {
        (row_i, col_i): float("inf")
        for row_i, row in enumerate(maze_map)
        for col_i in range(len(row))
    }
    # Costs from starting point to exit point through point (key).
    f_score = dict(g_score.items())
    # Default the move sequence costs to infinity

    g_score[starting_point] = 0
    f_score[starting_point] = _get_path_cost(starting_point, exit_point)

    # Track visited points and their costs using priority queue
    discovered_points = PriorityQueue()
    discovered_points.put(
        (
            _get_path_cost(starting_point, exit_point),
            _get_path_cost(starting_point, exit_point),
            starting_point,
        )
    )

    # The neighbor pairs are stored in a dictionary;
    # the values are the predecessors of the keys.
    neighbors = {}

    while not discovered_points.empty():
        current_pos = discovered_points.get()[2]
        # Found the exit, stop
        if current_pos == exit_point:
            break
        # Iterate through neighbor points
        for neighbor_point in _get_neighbors(maze_map, current_pos):
            temp_g_score = g_score[current_pos] + 1
            temp_f_score = temp_g_score + _get_path_cost(neighbor_point, exit_point)

            if temp_f_score < f_score[neighbor_point]:
                g_score[neighbor_point] = temp_g_score
                f_score[neighbor_point] = temp_f_score
                discovered_points.put(
                    (
                        temp_f_score,
                        _get_path_cost(neighbor_point, exit_point),
                        neighbor_point,
                    )
                )
                neighbors[neighbor_point] = current_pos

    path = _trace_path_from_exit(neighbors, exit_point, starting_point)
    return path


def _get_openings(maze_map: list, character: str) -> list:
    """Search and return positions of openings (exits or starts depending
    on value of `character`) from the edges of the maze.
    """
    in_first_col = [
        (row_i, 0) for row_i, row in enumerate(maze_map) if row[0] == character
    ]
    in_last_col = [
        (row_i, len(row) - 1)
        for row_i, row in enumerate(maze_map)
        if row[len(row) - 1] == character
    ]
    in_first_row = [
        (0, col_i) for col_i, char_ in enumerate(maze_map[0]) if char_ == character
    ]
    in_last_row = [
        (len(maze_map) - 1, col_i)
        for col_i, char_ in enumerate(maze_map[-1])
        if char_ == character
    ]
    if openings := in_first_col + in_last_col + in_first_row + in_last_row:
        return openings
    raise NotSolvableError(f"Maze not solvable: Missing {character}")


def find_paths(maze_map: list, max_moves: int) -> list:
    """Find cheapest path from each starting point to each exit point.
    :param maze_map: A list of strings that represents a maze.
    :param max_moves: The number of maximum moves to solve the maze.
    :return: A list of cheapest paths from start to exit: one for each
        solvable start-exit path.
    :rtype: list
    """
    paths = []
    for starting_point in _get_openings(maze_map, START):
        for exit_point in _get_openings(maze_map, EXIT):
            if path := _get_path(maze_map, starting_point, exit_point):
                if len(path) - 1 <= max_moves:  # Start point is not a move
                    paths.append(path)
    return paths


def read_maze_from_file(filepath: str) -> list:
    """Read maze representation from a .txt file.

    :param filepath: Absolute path of the file with the maze.
    :type filepath: str
    :raise: MazeParseError if file is not .txt, is not found or is empty.
    :return: A representation of the maze as a list of strings.
    :rtype: list(str)
    """
    if not os.path.exists(filepath):
        raise MazeParseError("Maze file not found! Plz give absolute path.")

    if not filepath.endswith(".txt"):
        raise MazeParseError("The file is in an unexpected format! Plz give .txt file.")

    with open(filepath, "r", encoding="utf-8") as maze_file:
        if lines := [line.strip("\n") for line in maze_file.readlines()]:
            return lines
        raise MazeParseError("Error parsing maze: Maze file empty!")


def parse_args(args: list) -> argparse.Namespace:
    """Parse arguments.
    :return: A argparse.Namespace instance with parsed arguments.
    """
    parser = argparse.ArgumentParser(
        prog="MazeSolver",
        description="MazeSolver is an amazing maze solver that solves any maze.",
    )
    parser.add_argument(
        "filepath", help="Absolute path to the file that contains the maze."
    )
    return parser.parse_args(args)


def solve(filepath: str, max_moves: int) -> tuple:
    """Solve a maze in a .txt file. Try to solve three times: with 20, 150 and 200
    maximum moves. Print the resulting path from start to exit and the count of
    moves used, or a message if the end could not be reached.
    :param filepath: Absolute path to a .txt file that contains the maze.
    :param max_moves: Maximum number of moves to solve the maze.
    """
    maze_map = read_maze_from_file(filepath)
    solutions = find_paths(maze_map, max_moves)
    best_path = min(solutions, key=len) if solutions else []
    for i, row in enumerate(maze_map):
        for j, _cell in enumerate(row):
            if (i, j) in best_path:
                row = list(row)
                row[j] = "\u2588"
                maze_map[i] = "".join(row)
    return best_path, maze_map


def main() -> None:
    """Try to solve a maze three times with increasing number
    of maximum moves and print the solution if found.
    """
    # Parse cli arguments (get file path)
    args = parse_args(sys.argv[1:])

    for max_moves in [38, 150, 200]:
        solution, solved_maze = solve(args.filepath, max_moves)
        if solution:
            moves = sum(row.count("\u2588") for row in solved_maze) - 2
            print(f"Found solution with <= {max_moves} ({moves} moves):")
            print("\n".join(solved_maze))
            break
        print(f"No solution found with <= {max_moves} moves.")


if __name__ == "__main__":
    main()
