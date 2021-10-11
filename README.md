# Homework Score Recorder

## Prerequisites and Installation steps
This script needs only Python 3.x, and MUST be run within a terminal.

Installation is as easy as cloning this repo and run `check.py` file.

## Manual instructions

### 1. Student list
Student list must be organized as a CSV format file `namelist.csv` as provided here. It's free to replace it with a new one with two columns of students' IDs and their names.

### 2. Operations
When this script is started, it automatically reads students' information from `namelist.csv` as described above. After this process is done, a prompt will appear on the screen.

#### 2.1 Normal input
Input one score entry with format:
```
[student-id(-suffix)] [score]<Enter>
```
For example, we can input `001 10<Enter>` to represent score 10 for student with ID SA21011001. The shorter suffix used, the higher probability multiple choices will occur.

#### 2.2 Delete entry
Delete one score entry with format:
```
[student-id(-suffix)] del<Enter>
```
Hint: `del` is reserved for deleting a score. If `del` is expected to be a valid score, the `DELETE_MANIPULATOR` variable of the main script has to be modified. I plan to make it a parameter from command line in the future.

#### 2.3 Show all entries
Show all entries with format:
```
s<Enter>
```

#### 2.4 Save and exit
Save and exit with format:
```
q<Enter>
```

