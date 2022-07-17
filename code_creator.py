import random


h = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', "I", 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
     'V', 'W', 'X', 'Y', 'Z',1,2,34,45,6,6,7,6,7,65,87,9,89,0,90,256,7,8,46,4]
def code():
    code = ""
    i = 0
    while i < 20:
        j = random.choice(h)
        code = code + str(j)
        i = i + 1
    code = "code:" + code

    return code