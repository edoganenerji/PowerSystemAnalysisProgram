from population import Population
import Transportv3
import random
import math
import psspy

class NSGA2Utils:

    def __init__(self, problem, each_of_bus_len,sav_ismi, ytim, regions, dfax_name, 
                 file_directory, tr_include, atr_include, manuel_definition ,num_of_individuals=100,
                 num_of_tour_particips=2, tournament_prob=0.9, crossover_param=0.8, mutation_param=0.02, tieLines=None):
        self.problem = problem
        self.num_of_individuals = num_of_individuals
        self.num_of_tour_particips = num_of_tour_particips
        self.tournament_prob = tournament_prob
        self.crossover_param = crossover_param
        self.mutation_param = mutation_param
        self.each_of_bus_len = each_of_bus_len
        self.sav_ismi = sav_ismi
        self.ytim = ytim
        self.regions = regions
        self.dfax_name = dfax_name
        self.file_directory = file_directory
        self.tr_include = tr_include 
        self.atr_include = atr_include
        self.manuel_definition = manuel_definition
        self.tieLines = tieLines
    def powerFlow(self):
        psspy.fdns([0,1,0,1,1,1,0,0])
        sol = psspy.solved()
        if sol > 0:
            psspy.fdns([0,1,0,1,1,0,0,0])
            sol = psspy.solved()
            if sol > 0:
                psspy.fnsl([0,0,0,1,1,1,0,0])
                psspy.fnsl([0,0,0,1,1,0,0,0])
                sol = psspy.solved()
        return sol
    def turn_bus_structure(self,individual, each_of_bus_len):
        turn_to_bus_format, next_pos, current_pos = [], 0, 0
        for i in range(len(each_of_bus_len)):
            next_pos += each_of_bus_len[i]
            turn_to_bus_format.append(individual.features[current_pos:next_pos])
            current_pos = next_pos
        return turn_to_bus_format
    
    def create_initial_population(self, start_pos, buses_included_zil_and_enough_line):
        population = Population()
        for i in range(self.num_of_individuals):
            individual = self.problem.generate_individual()
            if i == 0:
                individual.features = start_pos
            turn_to_bus_format_pre = self.turn_bus_structure(individual, self.each_of_bus_len)
            turn_to_bus_format = Transportv3.position_control(buses_included_zil_and_enough_line,turn_to_bus_format_pre, tr_include=True, atr_include=True)
            individual.features = [turn_to_bus_format[i][j] for i in range(len(turn_to_bus_format)) for j in range(len(turn_to_bus_format[i]))]
            _ = Transportv3.move_branch(turn_to_bus_format, buses_included_zil_and_enough_line, tr_include = self.tr_include, atr_include=self.atr_include)
            sol = self.powerFlow()
            if self.problem.tieLines is not None:
                psspy.save(self.file_directory+'\\'+self.sav_ismi+"_ReducedVersion_"+str(self.regions)+".sav")
                psspy.case(self.file_directory+"\\"+self.sav_ismi+".sav")        # Open Main Folder 
                psspy.progress_output(6,"",[0,0])
                _ = Transportv3.move_branch(turn_to_bus_format, buses_included_zil_and_enough_line, tr_include = self.tr_include, atr_include=self.atr_include)
                psspy.save(self.file_directory+'\\'+self.sav_ismi+".sav")
            self.problem.calculate_objectives(individual, sol)
            population.append(individual)
        return population

    def fast_nondominated_sort(self, population):
        population.fronts = [[]]
        for individual in population:
            individual.domination_count = 0
            individual.dominated_solutions = []
            for other_individual in population:
                if individual.dominates(other_individual):
                    individual.dominated_solutions.append(other_individual)
                elif other_individual.dominates(individual):
                    individual.domination_count += 1
            if individual.domination_count == 0:
                individual.rank = 0
                population.fronts[0].append(individual)
        i = 0
        while len(population.fronts[i]) > 0:
            temp = []
            for individual in population.fronts[i]:
                for other_individual in individual.dominated_solutions:
                    other_individual.domination_count -= 1
                    if other_individual.domination_count == 0:
                        other_individual.rank = i+1
                        temp.append(other_individual)
            i = i+1
            population.fronts.append(temp)

    def calculate_crowding_distance(self, front):
        if len(front) > 0:
            solutions_num = len(front)
            for individual in front:
                individual.crowding_distance = 0

            for m in range(len(front[0].objectives)):
                front.sort(key=lambda individual: individual.objectives[m])
                front[0].crowding_distance = 10**9
                front[solutions_num-1].crowding_distance = 10**9
                m_values = [individual.objectives[m] for individual in front]
                scale = max(m_values) - min(m_values)
                if scale == 0: scale = 1
                for i in range(1, solutions_num-1):
                    front[i].crowding_distance += (front[i+1].objectives[m] - front[i-1].objectives[m])/scale

    def crowding_operator(self, individual, other_individual):
        if (individual.rank < other_individual.rank) or \
            ((individual.rank == other_individual.rank) and (individual.crowding_distance > other_individual.crowding_distance)):
            return 1
        else:
            return -1

    def create_children(self, population, buses_included_zil_and_enough_line):
        children = []
        while len(children) < len(population):
            parent1 = self.__tournament(population)
            parent2 = parent1
            while parent1 == parent2:
                parent2 = self.__tournament(population)
            child1, child2 = self.__crossover(parent1, parent2)
            self.__mutate(child1)
            self.__mutate(child2)
            turn_to_bus_format1_pre = self.turn_bus_structure(child1, self.each_of_bus_len)
            turn_to_bus_format1 = Transportv3.position_control(buses_included_zil_and_enough_line,turn_to_bus_format1_pre, tr_include=True, atr_include=True)
            child1.features = [turn_to_bus_format1[i][j] for i in range(len(turn_to_bus_format1)) for j in range(len(turn_to_bus_format1[i]))]
            _ = Transportv3.move_branch(turn_to_bus_format1, buses_included_zil_and_enough_line, tr_include = self.tr_include, atr_include=self.atr_include)
            sol = self.powerFlow()
            if self.problem.tieLines is not None:
                psspy.save(self.file_directory+'\\'+self.sav_ismi+"_ReducedVersion_"+str(self.regions)+".sav")
                psspy.case(self.file_directory+"\\"+self.sav_ismi+".sav")        # Open Main Folder 
                psspy.progress_output(6,"",[0,0])
                _ = Transportv3.move_branch(turn_to_bus_format1, buses_included_zil_and_enough_line, tr_include = self.tr_include, atr_include=self.atr_include)
                psspy.save(self.file_directory+'\\'+self.sav_ismi+".sav")
            self.problem.calculate_objectives(child1, sol)
            turn_to_bus_format2_pre = self.turn_bus_structure(child2, self.each_of_bus_len)
            turn_to_bus_format2 = Transportv3.position_control(buses_included_zil_and_enough_line,turn_to_bus_format2_pre, tr_include=True, atr_include=True)
            child2.features = [turn_to_bus_format2[i][j] for i in range(len(turn_to_bus_format2)) for j in range(len(turn_to_bus_format2[i]))]
            _ = Transportv3.move_branch(turn_to_bus_format2, buses_included_zil_and_enough_line, tr_include = self.tr_include, atr_include=self.atr_include)
            sol = self.powerFlow()
            if self.problem.tieLines is not None:
                psspy.save(self.file_directory+'\\'+self.sav_ismi+"_ReducedVersion_"+str(self.regions)+".sav")
                psspy.case(self.file_directory+"\\"+self.sav_ismi+".sav")        # Open Main Folder 
                psspy.progress_output(6,"",[0,0])
                _ = Transportv3.move_branch(turn_to_bus_format2, buses_included_zil_and_enough_line, tr_include = self.tr_include, atr_include=self.atr_include)
                psspy.save(self.file_directory+'\\'+self.sav_ismi+".sav")
            self.problem.calculate_objectives(child2, sol)
            children.append(child1)
            children.append(child2)
        return children
    
    def tanh(self,x):
        return abs((math.exp(2*x)-1)/(math.exp(2*x)+1))
    
    def transfer_function_comparator(self,child_gene,tf_input):
        if self.tanh(tf_input) > random.uniform(0,1):
            if child_gene == 1:
                new_child_gene = 2
            else:
                new_child_gene = 1
        else:
            new_child_gene = child_gene
        return new_child_gene
    
    def __crossover(self, individual1, individual2):
        child1 = self.problem.generate_individual()
        child2 = self.problem.generate_individual()     
        child1.features = [individual1.features[i] if random.random() > self.crossover_param else individual2.features[i] for i in range(len(individual1.features))]
        child2.features = [individual1.features[i] if random.random() > self.crossover_param else individual2.features[i] for i in range(len(individual1.features))]
        #num_of_features = len(child1.features)
        #genes_indexes = range(num_of_features)
        #for i in genes_indexes:
            #beta = self.__get_beta()
            #x1 = (individual1.features[i] + individual2.features[i])/2
            #x2 = abs((individual1.features[i] - individual2.features[i])/2)
            #tr_function_input = x1 + beta*x2
            #child1.features[i] = self.transfer_function_comparator(child1.features[i], tr_function_input)
            #tr_function_input = x1 - beta*x2
            #child2.features[i] = self.transfer_function_comparator(child2.features[i], tr_function_input)
        return child1, child2

    def __get_beta(self):
        u = random.random()
        if u <= 0.5:
            return (2*u)**(1/(self.crossover_param+1))
        return (2*(1-u))**(-1/(self.crossover_param+1))

    def __mutate(self, child):
        num_of_features = len(child.features)
        for gene in range(num_of_features):
            if random.random() < self.mutation_param:
                if child.features[gene] == 1:
                    child.features[gene] = 2
                else:
                    child.features[gene] = 1
            #u, delta = self.__get_delta()
            #if u < 0.5:
                #new_gene = delta*(child.features[gene] - self.problem.variables_range[gene][0])
            #else:
                #new_gene = delta*(self.problem.variables_range[gene][1] - child.features[gene])
            #if new_gene < self.problem.variables_range[gene][0]:
                #child.features[gene] = self.problem.variables_range[gene][0]
            #elif new_gene > self.problem.variables_range[gene][1]:
                #child.features[gene] = self.problem.variables_range[gene][1]
            #else:
                #self.transfer_function_comparator(child.features[gene], new_gene)

    def __get_delta(self):
        u = random.random()
        if u < 0.5:
            return u, (2*u)**(1/(self.mutation_param + 1)) - 1
        return u, 1 - (2*(1-u))**(1/(self.mutation_param + 1))

    def __tournament(self, population):
        participants = random.sample(population.population, self.num_of_tour_particips)
        best = None
        for participant in participants:
            if best is None or (self.crowding_operator(participant, best) == 1 and self.__choose_with_prob(self.tournament_prob)):
                best = participant

        return best

    def __choose_with_prob(self, prob):
        if random.random() <= prob:
            return True
        return False
