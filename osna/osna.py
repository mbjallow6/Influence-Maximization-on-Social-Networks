import networkx as nx
from collections import Counter
import json
import os
import networkx as nx
import pandas as pd                                    # panda's nickname is pd
import numpy as np                                     # numpy as np
import time
import matplotlib.pyplot as plt

class algorithm:

    #SEED SELECTION FOR DEGREE CENTRALITY METHOD
    def degree_centrality_select_seed (self, graph, size):
        degrees = dict(graph.in_degree())
        degree_counts = dict(sorted(degrees.items(), key = lambda x:(-int(x[1]), int(x[0]))))
        seed = list(degree_counts.keys())[:size] #seed nodes
        return seed

    #INDEPENDENT CASCADE - SINGLE HOP
    def get_spread_magnitude_1hop(self, graph, seed):
        """
        Input:  graph object, set of seed nodes
        Output: number of nodes influenced by the seed nodes
        """
        nodes = seed.copy()
        # For each active node, find its neighbors that becomes influenced
        new_ones = [] 
        for node in nodes:
            # Determine those neighbors that become influenced
            new_inf_nodes = list(graph.predecessors(node))
            new_ones += new_inf_nodes

        all_infl_nodes = list(set(nodes + new_ones))
        return all_infl_nodes

    #INDEPENDENT CASCADE - MULTIPLE HOP
    def get_spread_magnitude_multi_hop(self, graph, seed):
        """
        Input:  graph object, set of seed nodes
        Output: number of nodes influenced by the seed nodes
        """
        nodes, all_infl_nodes = seed.copy(), seed.copy()
        while nodes:
            # For each newly active node, find its neighbors that becomes influenced
            new_ones = [] 
            for node in nodes:
                # Determine those neighbors that become influenced
                new_inf_nodes = list(graph.predecessors(node))
                new_ones += new_inf_nodes

            nodes = list(set(new_ones) - set(all_infl_nodes))
            all_infl_nodes += nodes

        return all_infl_nodes

    #ALL NEIGBHORS ARE ACTIVATED - EDGE WEIGHT ARE NOT CONSIDERED
    def LT_without_weight (self, graph, seed):
        nodes, all_infl_nodes = seed.copy(), seed.copy()
        while nodes:
            # For each newly active node, find its neighbors that becomes influenced
            new_ones = [] 
            for node in nodes:
                # Determine those neighbors that become influenced
                new_inf_nodes = list(graph.predecessors(node))
                new_ones += new_inf_nodes

            nodes = list(set(new_ones) - set(all_infl_nodes))
            all_infl_nodes += nodes
        return len(all_infl_nodes)

    #NEIGHBOURS WITH INFLUENCE GREATER THAN THRESHOLD GET INFLUENCED
    def LT_with_weight(self, graph, seed, threshold):
        influence_mag = {}  
        nodes, all_infl_nodes = seed.copy(), seed.copy()
        count = 0
        while nodes:
            # For each newly active node, find its neighbors
            new_ones = []
            for node in nodes:
                # Determine neighbors that become activated
                new_inf_nodes = []
                for follower in graph.predecessors(node):
                    if (follower not in nodes):
                        infl_by_node = graph.get_edge_data(follower,node)['weight']
                        if( infl_by_node >= threshold):
                            new_inf_nodes.append(follower)
                        elif((influence_mag.get(follower,0)+ infl_by_node) >= threshold ):
                            new_inf_nodes.append(follower)
                        else:
                            influence_mag[follower] = influence_mag.get(follower,0) + infl_by_node

                    new_ones += new_inf_nodes

            nodes = list(set(new_ones) - set(all_infl_nodes))
            # Adding newly activated nodes to the set of activated nodes
            all_infl_nodes += nodes
        #print("spread:", len(all_infl_nodes))

        return(len(all_infl_nodes))

    def celf(self, g, k, weightage, threshold = 0 ):  
        start_time = time.time()
        if(weightage):
            marg_gain = [(node, self.LT_with_weight(g,[node], threshold)) for node in list(g.nodes())]
        else:
            marg_gain = [(node, self.LT_without_weight(g,[node])) for node in list(g.nodes())]

        Q = sorted(marg_gain, key=lambda x: x[1],reverse=True)
        S = [Q[0][0]]
        spread = Q[0][1]
        list_of_spread = [Q[0][1]]
        Q = Q[1:]
        timelapse = [time.time()-start_time]

        # To Find k-1 nodes using sorting    
        while len(S)<k:

            stop = False

            while not stop:            
                #first node
                current = Q[0][0]

                #calculate spread for new seed
                if(weightage):
                    Q[0] = (current, self.LT_with_weight(g,S+[current], threshold) - spread)
                else:
                    Q[0] = (current, self.LT_without_weight(g,S+[current]) - spread)

                Q = sorted(Q, key = lambda x: x[1], reverse = True)
                #print("sorted Q: ", Q)

                # Check for top node
                stop = (Q[0][0] == current)

            # Select the next node
            spread += Q[0][1]
            S.append(Q[0][0])
            list_of_spread.append(spread)
            timelapse.append(time.time() - start_time)

            # Remove the selected node from the list
            Q = Q[1:]

        return(S,list_of_spread, timelapse)

    def import_json_create_graph(self, file_name):

        graph = nx.DiGraph()
        
        with open(file_name, "r") as infile:
            users = json.load(infile)
            for user in users:
                # Add a node
                graph.add_node(str(user['id']))
                # Add an edge to a follower
                #for follower in user['retweet_count'].keys():
                for follower in user['retweet_counts']:
                    #print(follower)
                    #print(user['id'], follower, user['influence_factor'][follower] )
                    graph.add_edge(follower, str(user['id']), weight = user['influence_factor'][follower])

        return graph