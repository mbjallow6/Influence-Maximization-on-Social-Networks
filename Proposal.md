## Overview

Examine 2 different approaches to find Maximum Influence in social network and compare results. In first approach, we calculate individual node popularity based on characteristics such as followers, views etc. and then compute influence magnitude for top K nodes. In second approach, we find well connected communities and their top influencers. From this set, best k 

influencers are chosen such that overall influence is maximum. Performance and outcomes of both methods are analysed for various scenarios. 

 

## Data

Data from Flickr, a website to share photographs. Data is collected using flickr API. 

Process of segmenting required components from raw data can pose problem.

## Method

Degree centrality and Page rank algorithms are used for approach 1. Clustering algorithms such as girvan newman is used for approach 2. 

We will be using exisiting library, modification are made based on graph requirement.

## Related Work

http://ilpubs.stanford.edu:8090/422/1/1999-66.pdf

https://dl.acm.org/citation.cfm?id=1935845

https://ieeexplore.ieee.org/document/6544543

https://www.computer.org/csdl/magazine/co/2013/04/mco2013040024/13rRUzp02jm

https://www.cs.purdue.edu/homes/ribeirob/pdf/Ribeiro_SamplingGraphsCDC12.pdf

## Evaluation

Compare influence magnitude of various algorithm implementation. Output table consists of Set of K nodes and their influence. 

