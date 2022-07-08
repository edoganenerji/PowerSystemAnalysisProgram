'''
Created on 24 Nis 2019

@author: erdidogan
'''
def search(x, nums):
    for i in range(len(nums)):
        if nums[i] == x:        # item found, return the index value
            return i
    return -1                   # loop finished, item was not in list
