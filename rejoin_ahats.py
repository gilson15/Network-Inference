
from __future__ import division
import numpy as np
import sys
import scipy.io
import matplotlib as mpl
import matplotlib.pyplot as plt
import networkx as nx
from colour import Color
from scipy.spatial import distance
from mpl_toolkits.axes_grid1 import ImageGrid

dataset = int(sys.argv[1])
aHatFileName = str(sys.argv[2])
inferredNetworkFileName = str(sys.argv[3])
N = int(sys.argv[4])
plot = False

if dataset != 0:
    filename = 'CRCNS/data/DataSet' + str(dataset) + '.mat'
    N = scipy.io.loadmat(filename)['data']['nNeurons'][0][0][0][0]
    x_array = scipy.io.loadmat(filename)['data']['x'][0][0][0]
    y_array = scipy.io.loadmat(filename)['data']['y'][0][0][0]


S_hat = np.zeros((N,N))

for i in range(N):
    filename = aHatFileName + str(i+1) + '.csv'
    S_hat[i] = np.genfromtxt(filename, delimiter=',')

# Transpose the inferred matrix
S_hat = S_hat.T

# Convert NaN to zeros
S_hat[np.where(np.isnan(S_hat))] = 0

# Remove values very close to zero
S_hat[np.where(S_hat <= np.percentile(S_hat,99, interpolation='lower'))] = 0

S_hat = np.interp(S_hat, np.linspace(S_hat.min(),S_hat.max(),1000), np.linspace(0,30,1000))

# S_hat[np.where(S_hat < 5)] = 0

if dataset != 0 and plot:
    DG = nx.DiGraph()
    for i in range(N):
        DG.add_node(i, pos=(x_array[i], y_array[i]))

inferred_network = []
color_map = []
red = Color('#f64f59')
colours = list(red.range_to(Color("#12c2e9"),7))
not_connected = []
for i, row in enumerate(S_hat):
    for j, col in enumerate(row):
        if col != 0:
            inferred_network.append([int(i), int(j), col])
            if dataset != 0 and plot:
                DG.add_weighted_edges_from([(int(j),int(i),col)])

np.savetxt(inferredNetworkFileName, inferred_network, delimiter=",")

# Check which nodes are connected
for k in range(N):
    if np.array(np.where(np.array(inferred_network) == k)).size == 0:
        not_connected.append(k)


if plot:
    senders = np.array(DG.edges)[:,0]
    senders_count = np.bincount(senders,minlength=N)
    receivers = np.array(DG.edges)[:,1]
    receivers_count = np.bincount(receivers,minlength=N)
    count = senders_count - receivers_count

    # Plot Indegree
    plt.figure()
    bins = np.linspace(0, 15, 12)
    plt.hist(senders_count,bins, label='outdegree', color='blue', alpha=0.5)
    plt.hist(receivers_count,bins, label='indegree', color='red', alpha=0.5)
    plt.xlabel('number of connections')
    plt.ylabel('number of occurrences')
    plt.title('Indegree and outdegree of the biological neural network')
    plt.grid()
    plt.legend()
    plt.savefig('plot/degree_histogram_real_network.pdf', dpi=300)
    plt.show()


    for k, i in enumerate(count):
        if k in np.array(not_connected):
            color_map.append(str('#ffbc98'))
        elif i <= -3:
            color_map.append(str(colours[0]))
        elif i == -2:
            color_map.append(str(colours[1]))
        elif i == -1:
            color_map.append(str(colours[2]))
        elif i == 0:
            color_map.append(str(colours[3]))
        elif i == 1:
            color_map.append(str(colours[4]))
        elif i == 2:
            color_map.append(str(colours[5]))
        elif i >= 3:
            color_map.append(str(colours[6]))
        
    if dataset != 0:
        pos=nx.get_node_attributes(DG,'pos')
        nx.draw(DG,pos, node_color=color_map)
        plt.title('Connectivity of a biological neural network')
        plt.savefig('plot/crcns_4_50_xy.pdf', dpi=300)
        plt.show()

    edges = np.array(DG.edges)
    distance_edges = np.zeros(edges.shape[0])

    # Compute the average edge distance
    for i in range(edges.shape[0]):
        distance_edges[i] = distance.euclidean(pos[np.array(DG.edges)[i,0]],pos[np.array(DG.edges)[i,1]])
    average_distance = np.mean(distance_edges)     
    print(str('Average edge distance is ' +  str(average_distance) + ' um'))
    positions = [pos[i] for i in range(N)] 
    min_x = min(np.array(positions)[:,0])
    min_y = min(np.array(positions)[:,1])
    max_x = max(np.array(positions)[:,0])
    max_y = max(np.array(positions)[:,1])
    print('Min x_axis = ', min_x)
    print('Max x_axis = ', max_x)
    print('Min y_axis = ', min_y)
    print('Max y_axis = ', max_y)
    positions = np.array(positions)
    distance_nodes = []
    for i in range(N):
        position_1 = positions[i]
        for j in range(N):
            if j != i:
                distance_nodes.append(distance.euclidean(positions[j],position_1))
    distance_nodes = np.array(distance_nodes)
    mean_distance_nodes = np.mean(distance_nodes)
    print('Mean distance between nodes is ', mean_distance_nodes)

    if dataset != 0:
        nx.draw(DG,node_color=color_map)
        plt.title('Connectivity of a biological neural network')
        plt.savefig('plot/crcns_4_50_xy_2.pdf', dpi=300)
        plt.show()
            
   
    d = dict(DG.degree)

    nx.draw(DG, pos=nx.spring_layout(DG),nodelist=d.keys(), node_size=[v * 99 for v in d.values()]) 
    plt.show()

    gamma = -2.5
    plt.figure()
    bins = np.linspace(0, 15, 12)
    plt.hist(senders_count + receivers_count ,bins, label='outdegree', color='blue', alpha=0.5)
    plt.plot(np.arange(15), np.arange(15)**gamma, 'r')
    plt.xlabel('number of connections')
    plt.ylabel('number of occurrences')
    plt.title('Number of connections of the biological neural network')
    plt.grid()
    plt.legend()
    plt.savefig('plot/connexions_histogram_real_network.pdf', dpi=300)
    plt.show()
