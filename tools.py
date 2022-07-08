#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Originally created by Jorge Mario Cruz Duarte in 2019 as a piece of customhys program
Some modifications were performed by Dr. Erdi DOĞAN in 2022.
'''
import json
from datetime import datetime
from os.path import exists as _check_path
from os import makedirs as _create_path
import numpy as np
class NumpyEncoder(json.JSONEncoder):
    """
    Numpy encoder
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)
        #return json.JSONEncoder.default(self, obj)
def _save_step(step_number, variable_to_save, regions):
    """
    This method saves all the information corresponding to specific step.

    :param int step_number:
        Value of the current step in the hyper-heuristic procedure. If it is not a hyper-heuristic, this integer
        corresponds to operator index.
    :param dict variable_to_save:
        Variables to save in dictionary format.
    :param int regions: 
        The number of the region chosen for optimal splitting. 
        For example, 702 represents bursa region.
    :return:
    :rtype:
    """

    # Define the folder name
    folder_name = r'BusLayoutResults//' + 'NSGA-II-' + str(regions)

    # Check if this path exists
    if not _check_path(folder_name):
        _create_path(folder_name)
        
    # Create a new file for this step
    with open(folder_name + f'/{step_number}-' + str(regions) + '.json', 'w') as json_file:
        json.dump(variable_to_save, json_file, cls=NumpyEncoder)
def _open_json(folder_name, json_name):
    # Check if this path exists
    if not _check_path(folder_name):
        _create_path(folder_name)
    with open(folder_name+'\\'+json_name, 'r') as json_file:
                file_data = json.load(json_file)
    return file_data
def _retrieve_overal_result(folder_name, json_name):
    """
    This method gets informations from json file 
    :param str folder_name:
        The file location of the created json file 
    :param str json_name:
        The name of the json file.
    :return: content of json file
    :rtype: Dictionary
    """
    return _open_json(folder_name, json_name)
def _determine_best_sol(folder_name, json_name, bcs = 1, verbose=False):
    """
    determine_best_sol is used to obtain the best set of solutions from the Pareto-front. 

    :param str folder_name:
        file location of json file
    
    :param str json_file:
        json file name
    """
    results = _retrieve_overal_result(folder_name, json_name)
    pareto_front_cost = results["best_cost_lists"][-1]
    pareto_front_pos = results["best_position_lists"][-1]
    cost1 = np.array([c[0] for c in pareto_front_cost])
    cost2 = np.array([c[1] for c in pareto_front_cost])
    #In order to ensure that all busbars are below their limits, the cost of 
    #short-circuit should be lower than 500
    suitable_solutions = np.where(cost1<500)[0]
    suitable_cost1 = cost1[suitable_solutions]
    suitable_cost2 = cost2[suitable_solutions]
    suitable_pos = [pareto_front_pos[i] for i in suitable_solutions]
    cost2SortedIndices = np.argsort(suitable_cost2)
    
    if bool(suitable_pos) == True:
        
        arg_bcs = cost2SortedIndices[int(bcs[-1])-1]
        best_compromise_position = suitable_pos[arg_bcs]
        if verbose == True:
            print ("Best compromise solution is ", [suitable_cost1[arg_bcs], suitable_cost2[cost2SortedIndices[arg_bcs]]])
            print ("Best compromise position is ", best_compromise_position)
    else:
        best_compromise_position = "There is no suitable solution obtained"
        suitable_cost1 = [None]
        suitable_cost2 = [None]
        arg_bcs = 0
    return best_compromise_position, [suitable_cost1[arg_bcs], suitable_cost2[arg_bcs]]