class Human(object):
    def __init__(self, name, height, weight, speed):
        self.name = name
        self.height = height
        self.weight = weight
        self.speed = speed

    def sayMyName(self):
        print 'My name is {}.'.format(self.name)

class Warrior(Human):
    def __init__(self):
        pass





Bob = Human('Bob', 70, 200, 8)
Karen = Human('Karen', 55, 150, 13)
print Bob.name
print Karen.name
