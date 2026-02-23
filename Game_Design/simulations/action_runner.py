import re
from Game_Design.dice_roller import *


def read_action(command: str) -> list:
    """
    parameter :command: R#XdYdlAeZ+-W
    ex1: 4d6dl2
    ex2: 2#3d12dl1e-5

    returns mandatorily the list with all possible
    commands, what is optional is with or N (N->None)
    return: ['R orN', 'X', 'Y', 'lA orN', 'Z orN', '+-W orN', 'False or True']
    ex1: ['None', '4', '6', 'l1', 'None', '0', 'True']
    ex2: ['2', '3', '12', 'l1', '12', '5', 'False']
    """
    command.strip()  # Transforms '4d6 + 5' -> '4d6+5'
    command.lower()  # Transforms '3d12Dl2' -> '3d12dl2'

    final_command = []
    index = 0
    reference_command = re.split(r'[#, d, e, +, -]', command)
    # reference_command:
    # ex1: [-- '4', '6', 'l1', -- '0']
    # ex2: ['2', '3', '12', 'l1', '12', '-5']
    # The split() method returns a list of substrings.
    if '#' in command:
        final_command.append(int(reference_command[index]))  # index=0
        index += 1  # index=1
    else:
        final_command.append(1)

    final_command.append(reference_command[index])  # X
    final_command.append(reference_command[index + 1])  # Y
    index += 2  # index=3

    if ('l' in command) or ('h' in command):
        final_command.append(reference_command[index])  # index=3
        index += 1  # index=4
    else:
        final_command.append(None)

    # Exploding Critical eZ or e ex: e8, e
    if 'e' in command:
        final_command.append(reference_command[index])  # index=4
        index += 1  # index=5
    else:
        final_command.append(None)

    # Modifier + or - ex: +3, -5
    addition = True
    if ('-' in command) or ('+' in command):
        final_command.append(reference_command[index])
        if '-' in command:
            addition = False
    else:
        final_command.append(0)
    final_command.append(addition)
    print(final_command)
    return final_command


def run_action(command: str):
    c = read_action(command)
    """
    return: ['R orN', 'X', 'Y', 'lA orN', 'Z orN', 'W orN', 'False or True']
                1      1     2     3         4        5            6

    WHICH roll to make is to consider only A and Z. 
        W only applies to the final result
        R is simply how many times to do it
    so the priority of what to define first is:
    l and h, A and Z | X and Y | W | R
         1           2     3   4 
    """
    rolls = []  # list of N-lists of results. Functions will have resolved advantages etc
    R = int(c[0])
    X = int(c[1])
    Y = int(c[2])
    function = roll_XdY
    D = False
    Z = False

    if c[4] is not None:
        Z = int(c[4])
        function = roll_XdY_eZ
    if c[3] is not None:
        pass

    for r in range(int(R)):
        rolls[r] = function(X, Y)

    pass


read_action("3d6")
