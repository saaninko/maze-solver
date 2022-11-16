import unittest
import os
from unittest import mock
from maze_solver import solve


class TestMazeSolver(unittest.TestCase):
    def test_get_openings_finds_single_starting_point(self):
        maze = ["########", "#######E", "#######^", "#########"]
        starting_points = solve._get_openings(maze, solve.START)
        self.assertEqual(starting_points, [(2, 7)])

    def test_get_openings_finds_single_exit_point(self):
        maze = ["########", "#######E", "#######^", "########"]
        ending_points = solve._get_openings(maze, solve.EXIT)
        self.assertEqual(ending_points, [(1, 7)])

    def test_get_openings_finds_multiple_starting_points(self):
        maze = ["#^^#####", "#######E", "#######E", "########"]
        starting_points = solve._get_openings(maze, solve.START)
        self.assertEqual(starting_points, [(0, 1), (0, 2)])

    def test_get_openings_finds_multiple_exit_points(self):
        maze = ["#^^#####", "#######E", "#######E", "########"]
        ending_points = solve._get_openings(maze, solve.EXIT)
        self.assertEqual(ending_points, [(1, 7), (2, 7)])

    def test_get_openings_raises_notsolvableerror_if_no_start_found(
        self,
    ):
        maze = ["######", "#######E", "#######E", "########"]
        with self.assertRaises(solve.NotSolvableError) as nse:
            solve._get_openings(maze, solve.START)
        self.assertEqual(str(nse.exception), "Maze not solvable: Missing ^")

    def test_get_openings_raises_notsolvableerror_if_no_exit_found(
        self,
    ):
        maze = ["######", "#######^", "########", "########"]
        with self.assertRaises(solve.NotSolvableError) as nse:
            solve._get_openings(maze, solve.EXIT)
        self.assertEqual(str(nse.exception), "Maze not solvable: Missing E")

    def test_trace_path_from_exit_returns_empty_dict_if_path_not_possible(self):
        exit = (1, 1)
        start = (3, 3)
        neighbors = {(3, 2): (3, 3), (2, 3): (3, 3), (2, 2): (2, 3)}
        self.assertEqual(solve._trace_path_from_exit(neighbors, exit, start), {})

    def test_trace_path_from_exit_finds_path_to_exit(self):
        exit = (1, 1)
        start = (3, 3)
        neighbors = {
            (2, 3): (3, 3),
            (3, 2): (3, 3),
            (1, 3): (2, 3),
            (3, 1): (3, 2),
            (2, 1): (3, 1),
            (1, 1): (2, 1),
        }
        self.assertEqual(
            solve._trace_path_from_exit(neighbors, exit, start),
            {
                (1, 1): None,
                (2, 1): (1, 1),
                (3, 1): (2, 1),
                (3, 2): (3, 1),
                (3, 3): (3, 2),
            },
        )

    def test_get_path_finds_shortest_path(self):
        maze = ["######E#", "#      #", "# #### #", "# #### #", "#      #", "######^#"]
        path = solve._get_path(maze, (4, 6), (1, 6))
        self.assertEqual(
            path, {(1, 6): None, (2, 6): (1, 6), (3, 6): (2, 6), (4, 6): (3, 6)}
        )

    def test_get_path_returns_empty_dict_if_no_path(self):
        maze = ["######E#", "# #    #", "# #### #", "# ######", "#      #", "######^#"]
        path = solve._get_path(maze, (4, 6), (1, 6))
        self.assertEqual(path, {})

    def test_get_path_cost_calculates_manhattan_distance(self):
        cost = solve._get_path_cost((0, 0), (6, 5))
        self.assertEqual(cost, 11)

    def test_get_path_cost_calculates_absolute_distance(self):
        cost = solve._get_path_cost((6, 5), (0, 0))
        self.assertEqual(cost, 11)

    def test_read_maze_from_file_raises_mazeparseerror_if_file_empty(self):
        filepath = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "data", "maze-empty.txt"
        )
        with self.assertRaises(solve.MazeParseError) as mpe:
            solve.read_maze_from_file(filepath)
        self.assertEqual(str(mpe.exception), "Error parsing maze: Maze file empty!")

    def test_read_maze_from_file_raises_mazeparseerror_if_file_not_txt(self):
        filepath = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "data", "maze-invalid.json"
        )
        with self.assertRaises(solve.MazeParseError) as mpe:
            solve.read_maze_from_file(filepath)
        self.assertEqual(
            str(mpe.exception),
            "The file is in an unexpected format! Plz give .txt file.",
        )

    def test_read_maze_from_file_raises_mazeparseerror_if_file_not_found(self):
        with self.assertRaises(solve.MazeParseError) as mpe:
            solve.read_maze_from_file("no_such_file.txt")
        self.assertEqual(
            str(mpe.exception), "Maze file not found! Plz give absolute path."
        )

    def test_read_maze_from_file_forms_correct_maze(self):
        filepath = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "data", "maze-task-first.txt"
        )
        self.assertEqual(
            solve.read_maze_from_file(filepath),
            [
                "#######E########E####################",
                "# ### #   ###### #    #     #     # E",
                "# ### ### #      #  #    #     #    #",
                "# ### # # # ###### ##################",
                "#            #       #    #   #   # #",
                "#  # ##      # ##### #  # # # # # # #",
                "#  #         #   #   #  # # # # #   #",
                "#  ######   ###  #  ### # # # # ### #",
                "#  #    #               #   #   #   #",
                "#  # ## ########   ## ###########   #",
                "#    ##          ###                #",
                "# ## #############  ###   ####   ## #",
                "#  ### ##         #  #  #           #",
                "#  #   ## ####     #    #      ###  #",
                "#  # #### #  #     #    #####       #",
                "#  #      #      ###           ##   #",
                "#  #####           #   ##   #   #   #",
                "#                                   #",
                "##################^##################",
            ],
        )

    def test_parse_args_raises_systemexit_if_filepath_missing(self):
        with self.assertRaises(SystemExit):
            solve.parse_args([])

    def test_parse_args_parses_filepath_arg(self):
        args = solve.parse_args(["test_file"])
        self.assertEqual(args.filepath, "test_file")

    @mock.patch("maze_solver.solve._get_path")
    def test_find_paths_returns_empty_list_if_no_paths_found(
        self, mock_get_paths
    ):
        mock_maze = ["##^E###", "########", "########", "########"]
        mock_get_paths.return_value = []
        self.assertEqual(solve.find_paths(mock_maze, 100), [])

    @mock.patch("maze_solver.solve._get_path")
    def test_find_paths_returns_path_if_len_less_than_max_moves(self, mock_get_path):
        mock_maze = ["##^E###", "########", "########", "########"]
        mock_path = {1: 1, 2: 2, 3: 3}
        mock_get_path.return_value = mock_path
        self.assertEqual(solve.find_paths(mock_maze, 4), [mock_path])

    @mock.patch("maze_solver.solve._get_path")
    def test_find_paths_discards_path_if_len_greater_than_max_moves(
        self, mock_get_path
    ):
        mock_maze = ["##^E###", "########", "########", "########"]
        mock_get_path.return_value = {1: 1, 2: 2, 3: 3, 4: 4}
        self.assertEqual(solve.find_paths(mock_maze, 2), [])

    @mock.patch("maze_solver.solve._get_path")
    def test_find_paths_returns_path_if_len_equal_to_max_moves(self, mock_get_path):
        mock_maze = ["##^E###", "########", "########", "########"]
        mock_path = {1: 1, 2: 2, 3: 3}
        mock_get_path.return_value = mock_path
        self.assertEqual(solve.find_paths(mock_maze, 2), [mock_path])

    def test_solve_returns_printable_solution_for_solvable_maze(self):
        best_path, maze_map = solve.solve(
            filepath=os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "data",
                "maze-task-first.txt",
            ), max_moves=100
        )
        solution = [
            "#######█########E####################",
            "# ### #███###### #    #     #     # E",
            "# ### ###█#      #  #    #     #    #",
            "# ### # #█# ###### ##################",
            "#        ███ #       #    #   #   # #",
            "#  # ##    █ # ##### #  # # # # # # #",
            "#  #       █ #   #   #  # # # # #   #",
            "#  ######  █###  #  ### # # # # ### #",
            "#  #    #  ███████████  #   #   #   #",
            "#  # ## ########   ##█###########   #",
            "#    ##          ### ███            #",
            "# ## #############  ###█  ####   ## #",
            "#  ### ##         #  #██#           #",
            "#  #   ## ####     #███ #      ###  #",
            "#  # #### #  #     #█   #####       #",
            "#  #      #      ###█          ##   #",
            "#  #####           #█  ##   #   #   #",
            "#                 ███               #",
            "##################█##################",
        ]
        self.assertEqual(
            maze_map, solution
        )

