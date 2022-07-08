from utils import NSGA2Utils
from population import Population
from time import perf_counter
class Evolution:

    def __init__(self, problem, start_pos, each_of_bus_len, buses_included_zil_and_enough_line, sav_ismi, ytim, regions, dfax_name, file_directory, tr_include, atr_include, manuel_definition,
                num_of_individuals=100, num_of_tour_particips=2, tournament_prob=0.9, crossover_param=0.8, mutation_param=0.02):
        self.utils = NSGA2Utils(problem, each_of_bus_len,sav_ismi, ytim, regions, dfax_name, file_directory, tr_include, atr_include, manuel_definition, num_of_individuals, num_of_tour_particips, tournament_prob, crossover_param, mutation_param)
        self.population = None
        self.on_generation_finished = []
        self.num_of_individuals = num_of_individuals
        self.start_pos = start_pos
        self.buses_included_zil_and_enough_line = buses_included_zil_and_enough_line
        self.best_pos_front_list_each_epoch = []
        self.best_cost_front_list_each_epoch = []
        self.epoch_time = []
        self.all_population_list = []
        self.all_cost_list = []

    def evolve(self, current_iteration):
        self.current_iteration = current_iteration
        if current_iteration == 0:
            self.population = self.utils.create_initial_population(self.start_pos, self.buses_included_zil_and_enough_line)
            self.all_population_list.append([gen.features for gen in self.population.population])
            self.all_cost_list.append([gen.objectives for gen in self.population.population])
            self.utils.fast_nondominated_sort(self.population)
            for front in self.population.fronts:
                self.utils.calculate_crowding_distance(front)
        t0 = perf_counter() 
        children = self.utils.create_children(self.population, self.buses_included_zil_and_enough_line)
        self.population.extend(children)
        self.utils.fast_nondominated_sort(self.population)
        new_population = Population()
        front_num = 0
        while len(new_population) + len(self.population.fronts[front_num]) <= self.num_of_individuals:
            self.utils.calculate_crowding_distance(self.population.fronts[front_num])
            new_population.extend(self.population.fronts[front_num])
            front_num += 1
        self.utils.calculate_crowding_distance(self.population.fronts[front_num])
        self.population.fronts[front_num].sort(key=lambda individual: individual.crowding_distance, reverse=True)
        new_population.extend(self.population.fronts[front_num][0:self.num_of_individuals-len(new_population)])
        returned_population = self.population
        self.population = new_population
        self.utils.fast_nondominated_sort(self.population)
        for front in self.population.fronts:
            self.utils.calculate_crowding_distance(front)
        print("\n\nThe best front for Generation number ", current_iteration+1, " is")
        Data_prepare_sol, Data_prepare_obj = [], []
        count = 0
        for firsfront in returned_population.fronts[0]:
            print(firsfront.features)
            print (firsfront.objectives)
            Data_prepare_sol.append(firsfront.features)
            Data_prepare_obj.append(firsfront.objectives)
            count += 1
        self.best_pos_front_list_each_epoch.append(Data_prepare_sol)
        self.best_cost_front_list_each_epoch.append(Data_prepare_obj)
        pos_list, cost_list = [], []
        for gen in self.population.population:
            pos_list.append(gen.features)
            cost_list.append(gen.objectives)
        self.all_population_list.append(pos_list)
        self.all_cost_list.append(cost_list)
        t1 = perf_counter() 
        self.epoch_time.append(t1-t0)
        return returned_population.fronts[0]
