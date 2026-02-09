from random import randint

"""
Many functions were inspired by the Discord bot rollem

4d6 -- sum of 4 6-sided dice
4#d6 -- 4 rolls of 1d6

4d6dl1 -- drop the lowest and sum the rest

4d6dh1  -- drop the highest and sum the rest

6#4d6 -- 6 rolls of 4d6
"""

"""
Simulates rolling 'x' dice with 'y' sides.

Args:
    x (int): number of dice to be rolled.
    y (int): number of sides of each die.

Returns:
    list: A list of integers with the results of each die.
"""

def roll_XdY(x, y):
    return list((randint(1, y)) for _ in range(x))

# drop the Z lowest result
def roll_XdYdl_Z(x, y, z):
    rolls_sort = sorted(roll_XdY(x, y))
    for _ in range(z):
        rolls_sort.pop(0)
    return rolls_sort

def roll_XdYdh_Z(x, y, z):
    rolls_sort = sorted(roll_XdY(x, y), reverse=True)
    for _ in range(z):
        rolls_sort.pop(0)
    return rolls_sort

# roll XdY exploding at Z and above
def roll_XdY_eZ(x, y, z):
    result = roll_XdY(x, y)
    soma = sum(result)
    if result[0] >= z:
        soma += roll_XdY_eZ(x, y, z)
    return soma

# roll XdY, missing in an 1 and criting in the max value of the die
def roll_Nimble(x, y, vicious=False):
    roll = roll_XdY(x, y)
    soma = sum(roll)
    if roll[0] == y:
        print("Crit")
        if not vicious:
            soma += roll_XdY_eZ(1, y, y)
        else:
            soma += roll_XdY_eZ(2, y, y)
        pass
    elif roll[0] == 1:
        print("Miss")
        return 0
    return soma

def roll_witcher_1d10(base=0):
    roll = roll_XdY(1, 10)
    base += roll[0]
    explode = roll_XdY_eZ(1, 10, 10)
    if roll[0] == 10:
        base += explode
    elif roll[0] == 1:
        base -= explode
    return base
    pass

#print(roll_Nimble(4, 4, True))
#print(roll_witcher_1d10(5))