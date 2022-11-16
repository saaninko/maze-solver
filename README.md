## Maze Solver

Maze solver solves any maze with a little help from A* search algorithm.

The maze should be in .txt format and the structure of the maze follows the following rules:
- Character `#` represents a block in the maze
- Whitespace character represents movable space
- Character `E` represents an exit point
- Character `^` represents a starting point
- The edges of the maze can only contain exit or entry points (in addition to `#`)
    and there should not be any extra characters outside of the maze

### Usage

1) Clone this repo

    ```
    cd ~
    git clone https://github.com/saaninko/maze-solver.git
    ```

2) Install maze solver

    ```
    cd ~/maze-solver
    pip install .
    ```

2) To run maze solver, run command `solve` and give the path to the maze file as command line argument

    ```
    solve /path/to/file
    ```
    
    The file `tests/data/maze-task-first.txt` contains an example of a valid maze format.

    Try it:
    ```
    solve ~/maze-solver/tests/data/maze-task-first.txt
    ```

### Tests

Maze solver has some unit tests which can be run with:

```
python -m unittest -b tests/test_solve.py
```