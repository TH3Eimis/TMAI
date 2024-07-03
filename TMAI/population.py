import random
import matplotlib.pyplot as plt
from agent import Agent

DEFAULT_POPULATION_SIZE = 3
CROSS_GENE_CAP = 4
CROSS_GENE_DECREASE = 2
ELITISM_PERCENTAGE = 5

class Population:
    '''Contains the population of [SIZE] and completes mutations and crossover needed varaibles, size can be passed as param, default is 100'''

    def __init__(self, size=DEFAULT_POPULATION_SIZE):
        self.size = size
        self.individuals = []

    def __str__(self,include_individuals=False):
        if include_individuals:
            return f"Population size: {self.size}, individuals: {self.individuals}"
        else:
            return f"Population size: {self.size}"

    def createPop(self,agent_class):
        for i in range(self.size):
            # Create a new agent and add it to the population
            self.individuals.append(agent_class(id=i))

    def evalFitness(self):
        for individual in self.individuals:
            # Evaluate the fitness of each individual
            print(f"individual id is {individual.agent_id}")
            print(f"individual fitness is {individual.fitness.value}")
            individual.fitness.value = individual.fitness.evaluate()
            print(f"new individual fitness is {individual.fitness.value}")

    def selectParent(self,in_gestation):
        # Select parents based on fitness
        parents = random.choices([ind for ind in self.individuals if ind not in in_gestation], k=2)
        in_gestation.append(parents[0])
        in_gestation.append(parents[1])
        return parents

    def crossover(self,new_pop):
        in_gestation = []
        for _ in range(int(self.size/2)):
            parents = self.selectParent(in_gestation)

            offspring1 = parents[0].__class__(id=parents[0].agent_id)
            offspring2 = parents[1].__class__(id=parents[1].agent_id)
            # Perform crossover
            
            random_index = random.randint(0, len(parents[0].genes))
            print(random_index)
            random_index = random_index - CROSS_GENE_DECREASE if random_index > CROSS_GENE_CAP else random_index
            print(random_index)
            selected_genes = random.sample(parents[0].genes.keys(), random_index)

            parents[0].genes = {key: parents[0].genes[key] for key in parents[0].genes if key not in selected_genes}
            offspring2.genes.update({key: parents[0].genes[key] for key in parents[0].genes if key in selected_genes})

            parents[1].genes = {key: parents[1].genes[key] for key in parents[1].genes if key not in selected_genes}
            offspring1.genes.update({key: parents[1].genes[key] for key in parents[1].genes if key in selected_genes})

            in_gestation.append(parents[0])
            in_gestation.append(parents[1])

            new_pop.append(offspring1)
            new_pop.append(offspring2)
        return new_pop
        # available_genes = list('max_speed',
        #     'acceleration',
        #     'steer',
        #     'crash_threshold')
        

    def mutate(self):
        for individual in self.individuals:
            if random.random() > individual.genes['mutation_rate']:
                gene = random.choice(list(individual.genes.keys()))
                match gene:
                    case 'max_speed':
                        individual.genes[gene] = random.uniform(0.0, 1.0)
                    case 'acceleration':
                        individual.genes[gene] = random.uniform(0.0, 1.0)
                    case 'steer':
                        individual.genes[gene] = random.uniform(-1.0, 1.0)
                    case 'crash_threshold':
                        individual.genes[gene] = random.uniform(0.0, 10.0)
                    case 'mutation_rate':
                        individual.genes[gene] = random.uniform(0.0, 1.0)
                    case _:
                        print("Invalid gene to mutate")
                        pass
            else:
                continue

    def elitism(self, new_pop):
        # Sort individuals by fitness in descending order
        self.individuals.sort(key=lambda x: x.fitness.value, reverse=True)
        # Keep EP of best individuals
        best_individuals = self.individuals[:int(self.size/ELITISM_PERCENTAGE)]
        print(f"best individuals are {best_individuals}")
        new_pop.extend(best_individuals)

    def evolve(self):
        # Evaluate fitness # Perform elitism # Select parents and perform crossover
        new_population = []

        self.elitism(new_population)

        new_population = self.crossover(new_population)

        # Replace entire population with offspring
        self.individuals = new_population

        # Mutate the population
        self.mutate()


        

    # Plotting the fitness of each agent
    def plotFitness(self,fitlist):
        agents_fitness = fitlist
        plt.figure()
        plt.bar(range(len(self.individuals)), agents_fitness)
        plt.xlabel('Agent ID')
        plt.xticks(range(len(self.individuals)), range(len(self.individuals)))
        plt.ylabel('Fitness')
        plt.title('Fitness of Each Agent')
        plt.show()


# if __name__=="__main__":
#     print("Population module loaded successfully")
#     pop = Population()
#     pop.createPop(Agent)
#     pop.crossover()
#     # print(pop.__str__(True))