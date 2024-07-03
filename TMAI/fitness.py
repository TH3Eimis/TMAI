AVG_SPEED_ENUM = {
    'slow': 25,
    'medium': 40,
    'fast': 60,
}

class Fitness:
    '''Contain fitness of an agent and is able to alter the fitness value '''

    def __init__(self,agent):
        self.owner = agent
        self.value = 0.0
        self.time_taken = 0.0
        self.crashes = 0
        self.rewards = []
        self.medal_times = {}
        self.average_speed = 0.0


    def setFitness(self, num):
        self.value = num

    def calcFitness(self, num):
        self.value = self.value + num

    def evaluate(self):
        match self.time_taken:
            case _ if self.medal_times["author"] > self.time_taken:
                self.value += 10.0
            case _ if self.medal_times["gold"] > self.time_taken:
                self.value += 5.0
            case _ if self.medal_times["silver"] > self.time_taken:
                self.value += 3.5
            case _ if self.medal_times["bronze"] > self.time_taken:
                self.value += 2.0
            case _:
                self.value -= 1.0

        self.calcRewards()
        self.calcCrashes()
        self.calc_average_speed()
        match self.average_speed:
            case _ if self.average_speed > AVG_SPEED_ENUM['fast']:
                self.value += 1.0
            case _ if self.average_speed > AVG_SPEED_ENUM['medium']:
                self.value += 0.5

    def calc_average_speed(self):
        self.average_speed = float((((self.average_speed)/100) / self.time_taken))

    def calcRewards(self):
            total = 0
            for reward in self.rewards:
                total += {
                    'finish': 1.0,
                }.get(reward, 0)
            self.value += total
    
    def calcCrashes(self):
        self.value += 1.0 - (0.2 * self.crashes)