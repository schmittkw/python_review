class Human(object):
    def __init__(self, name, height, weight, speed):
        self.name = name
        self.height = height
        self.weight = weight
        self.speed = speed
        self.strength = 10
        self.health = 100

    def sayMyName(self):
        print 'My name is {}.'.format(self.name)
    
    def attack(self, monster):
        if type(monster) is Monster:
            monster.health -= 25
            print "{} attacked {} for 25 health.".format(self.name, monster.name)
            print "{}'s health was reduced to {}.".format(monster.name, monster.health)
        else:
            print "You can only attack monsters"
        return self

class Warrior(Human):
    def __init__(self, name, height, weight, speed):
        super(Warrior, self).__init__(name, height, weight, speed)
        self.strength = 30
        self.health = 150

class Monster(Human):
    def __init__(self,name,height,weight,speed):
        super(Monster, self).__init__(name, height, weight, speed)





Bob = Human('Bob', 70, 200, 8)
Karen = Human('Karen', 55, 150, 13)
warrior = Warrior('Thrall', 80, 300, 5)
monster = Monster('Grunt', 90, 325, 8)

# warrior.attack(monster).attack(monster)
for i in range(3,6):
    warrior.attack(monster)