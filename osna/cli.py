# -*- coding: utf-8 -*-

"""Console script for elevate_osna."""

# add whatever imports you need.
# be sure to also add to requirements.txt so I can install them.
import click
import json
import glob
import pickle
import sys

import numpy as np
import os
import pandas as pd
import re
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, classification_report

from . import credentials_path, clf_path
from .mytwitter import Twitter
from .osna import algorithm

@click.group()
def main(args=None):
    """Console script for osna."""
    return 0

@main.command('collect')
@click.argument('directory', type=click.Path(exists=True))
def collect(directory):
    """
    Collect data and store in given directory.

    This should collect any data needed to train and evaluate your approach.
    This may be a long-running job (e.g., maybe you run this command and let it go for a week).
    """
    twitter = Twitter()
    
    fname = directory + os.path.sep + 'data.json'
    outf = open(fname, 'wt')
    
    baseUsers_screenname = ['nickjonas','haileybieber','shakira','britneyspears','shakira','Cristiano','rihanna','MatthewPerry','justinbieber','JLo', 'pitbull', 'ShawnMendes']
    
    baseUsers = twitter._get_users('screen_name', baseUsers_screenname)
    twitter.add_followers(baseUsers)
    twitter._add_tweets(baseUsers)
    twitter.add_retweet_ids(baseUsers)
    twitter.add_influence_factor(baseUsers)
    outf.write(json.dumps(baseUsers, ensure_ascii=False) + '\n')
    outf.close()
	
@main.command('evaluate')
@click.argument('filename', type=click.Path(exists=True))
def evaluate(filename):
    """
    Report accuracy and other metrics of your approach.
    For example, compare classification accuracy for different
    methods.
    """
    g = algorithm()
    src_path = filename
	
    G = g.import_json_create_graph(filename)
    print("****************** EXECUTION RESULT **************")
    k = 10
    start_time = time.time()
    d_seed = g.degree_centrality_select_seed(G, k)
    print("Seed Count: ", k)
    print("\n")
    print('OUTPUT OF DEGREE CENTRALITY ALGORITHM')
    print("seed: ", d_seed)
    d_time = [time.time()-start_time]
    print("****************** EXECUTION RESULT **************")
    k = 10
    start_time = time.time()
    d_seed = g.degree_centrality_select_seed(G, k)
    print("Seed Count: ", k)
    print("\n")
    print('OUTPUT OF DEGREE CENTRALITY ALGORITHM')
    print("seed: ", d_seed)
    d_time = [time.time()-start_time]

    d_inf_nodes = g.get_spread_magnitude_multi_hop(G, d_seed)
    print("Spread Magnitude: ", d_inf_nodes)
    print("Computation Time:", d_time)

    #print("Multi hop spread for seed: ", spread2)
    print("\n")
    print('OUTPUT OF CELF')
    celf_seed, celf_inf_nodes, celf_time = g.celf(G, k, False)
    print("celf seed: ", celf_seed)
    print("celf spread: ", celf_inf_nodes)
    print("Computation time: ", celf_time)
    print("\n")

    print('OUTPUT OF WEIGHTED CELF')
    w_celf_seed, w_celf_inf_nodes, w_celf_time = g.celf(G, k, True, 0.1)
    print("weighted celf seed: ", w_celf_seed)
    print("weighted celf spread: ", w_celf_inf_nodes)
    print("Computation time: ", w_celf_time)
    print("\n")

    print('OUTPUT OF WEIGHTED CELF - WITH DIFFERENT THRESHOLD')
    threshold = 0.05
    w_celf_seed1, w_celf_inf_nodes1, w_celf_time1= g.celf(G, k, True, threshold)
    print("Threshold: ", threshold )
    print("weighted celf seed: ", w_celf_seed1)
    print("weighted celf spread: ", w_celf_inf_nodes1)
    print("Computation time: ", w_celf_time1)
    print("\n")

    threshold = 0.075
    w_celf_seed2, w_celf_inf_nodes2, w_celf_time2 = g.celf(G, k, True, threshold)
    print("Threshold: ", threshold )
    print("weighted celf seed: ", w_celf_seed2)
    print("weighted celf spread: ", w_celf_inf_nodes2)
    print("Computation time: ", w_celf_time2)
    print("\n")

    threshold = 0.1
    w_celf_seed3, w_celf_inf_nodes3, w_celf_time3 = g.celf(G, k, True, threshold)
    print("Threshold: ", threshold )
    print("weighted celf seed: ", w_celf_seed3)
    print("weighted celf spread: ", w_celf_inf_nodes3)
    print("Computation time: ", w_celf_time3)
    print("\n")

    threshold = 0.15
    w_celf_seed4, w_celf_inf_nodes4, w_celf_time4 = g.celf(G, k, True, threshold )
    print("Threshold: ", threshold )
    print("weighted celf seed: ", w_celf_seed4)
    print("weighted celf spread: ", w_celf_inf_nodes4)
    print("Computation time: ", w_celf_time4)
    print("\n")

    threshold = 0.2
    w_celf_seed5, w_celf_inf_nodes5, w_celf_time5= g.celf(G, k, True, threshold )
    print("Threshold: ", threshold )
    print("weighted celf seed: ", w_celf_seed5)
    print("weighted celf spread: ", w_celf_inf_nodes5)
    print("Computation time: ", w_celf_time5)
    print("\n")

    print("**************************************")
    x = [k+1 for k in range(k)]
    deg_inf_nodes = [d_inf_nodes for i in range(k)]
    fig, ax = plt.subplots()
    ax.plot(x, deg_inf_nodes, 'r--', label='Degree centrality')
    ax.plot(x, celf_inf_nodes, 'bs', label='CELF')
    ax.plot(x, w_celf_inf_nodes, 'g^', label='Weighted CELF')
    plt.xlabel('Seed')
    plt.ylabel('Spread Magnitude')
    plt.title("Spread magnitude Vs Seed size for different algorithms")
    leg = ax.legend();

@main.command('network')
def network():
    """
    Perform the network analysis component of your project.
    E.g., compute network statistics, perform clustering
    or link prediction, etc.
    """
    pass

@main.command('stats')
@click.argument('directory', type=click.Path(exists=True))
def stats(directory):
    """
    Read all data and print statistics.
    E.g., how many messages/users, time range, number of terms/tokens, etc.
    """
    print('reading from %s' % directory)
    # use glob to iterate all files matching desired pattern (e.g., .json files).
    # recursively search subdirectories.


@main.command('train')
@click.argument('directory', type=click.Path(exists=True))
def train(directory):
    """
    Train a classifier on all of your labeled data and save it for later
    use in the web app. You should use the pickle library to read/write
    Python objects to files. You should also reference the `clf_path`
    variable, defined in __init__.py, to locate the file.
    """
    print('reading from %s' % directory)
    # (1) Read the data...
    #
    # (2) Create classifier and vectorizer.
    # You can use any classifier you like.
    clf = LogisticRegression() # set best parameters 
    vec = CountVectorizer()    # set best parameters

    # save the classifier
    pickle.dump((clf, vec), open(clf_path, 'wb'))



@main.command('web')
@click.option('-t', '--twitter-credentials', required=False, type=click.Path(exists=True), show_default=True, default=credentials_path, help='a json file of twitter tokens')
@click.option('-p', '--port', required=False, default=9999, show_default=True, help='port of web server')
def web(twitter_credentials, port):
    """
    Launch a web app for your project demo.
    """
    from .app import app
    app.run(host='0.0.0.0', debug=True, port=port)
    
    


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
