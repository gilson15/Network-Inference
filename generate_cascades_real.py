import scipy.io
import numpy as np
import os

dataset = int(sys.argv[1])
indicesFileName = str(sys.argv[2])
firingsFileName = str(sys.argv[3])
diffusion_type = str(sys.argv[4])
horizon = int(sys.argv[5])
simulation_duration = int(sys.argv[6])*1000
cascadesFileName = str(sys.argv[7])
aBadFileName = str(sys.argv[8])
aPotentialFileName = str(sys.argv[9])
numCascadesFileName = str(sys.argv[10])
cascadeOption = str(sys.argv[11])
numFiringsFileName = str(sys.argv[12])


# Load the data
filename = 'CRCNS/data/DataSet' + str(dataset) + '.mat'
data = scipy.io.loadmat(filename)['data']
NUMBER_NEURONS = data['nNeurons'][0][0][0][0]
N = NUMBER_NEURONS
simulation_duration = data['recordinglength'][0][0][0][0]
diffusion_type = 'rayleigh'
cascadeOption='maximum_cascades'

horizon = 20

num_cascades = np.zeros(N);
A_potential = np.zeros((N,N));
A_bad = np.zeros((N,N));
A_hat = np.zeros((N,N));

spikes = []

# This is needed to create a firings and indices file
for i in range(0,NUMBER_NEURONS):
    spikes.append(data['spikes'][0][0][i][0][0])

    # Flatten the firing times from each of the neurons
    firings = [item for sublist in spikes for item in sublist]

    # Create the indices where each row is a different index
    indices = [[i+1]*len(spikes[i]) for i in range(len(spikes))]

    # Flatten the indices from each of the spikes
    indices = [item for sublist in indices for item in sublist]

    # Order the firings and indices chronologically
    sort_idx = np.argsort(firings)
    firings = [firings[sort_idx[i]] for i in range(len(firings))]
    indices = [indices[sort_idx[i]] for i in range(len(indices))]


n = 0
m = 0
x = 0
start = firings[n]
cascades = np.ones((int(simulation_duration/horizon),N))*(-1)

if cascadeOption == 'maximum_cascades' or cascadeOption == 'maximum_independence': 

    # Iterate through the simulation spikes
    while n < len(firings):
        
        if n != 0 and (n > x*10):
            print(x*10)
            x = x + 1

        # define the window f observation
        start = firings[n] 
        end = start + horizon

        # Only count the cascade if it had previously reached a steady state
        if cascadeOption == 'maximum_independence':
            if n > 0 and np.diff(firings)[n-1] < horizon:

               n = n + 1
               continue 

        index = np.array(np.where((firings >= start) & (firings < end)))[0]

        firings_in_window = [firings[i] for i in index]
        firings_in_window = firings_in_window - start
        indices_in_window = [indices[i] for i in index]

        # initialise a cascade, non-fired with -1; assume all non-fired
        current_cascade = np.ones(N)*(-1)

        # first neuron to spike starts the cascade
        current_cascade[indices_in_window[0]-1] = 0

        # update cascade based on the rest of the firings
        for k in range(len(indices_in_window)):
            
            # Only the first firing is taken into account
            if current_cascade[indices_in_window[k]-1] == -1:
                current_cascade[indices_in_window[k]-1] = firings_in_window[k]    

        # Don't count the cascades where only one node fires
        if np.bincount(current_cascade.astype(int) + 1)[0] < N - 1:
            cascades[m] = current_cascade
            m = m + 1 

        # The index of the firing that starts the next cascade is the one following the last firing of this cascade 
        n = index[-1] + 1

    # Delete the cascades with no entries (they were initialized with all -1s)
    cascades = cascades[0:np.where(cascades == 0)[0][-1] + 1]
    # print('Number of cascades: ', m)


x = 0

# Iterate through all the cascades
for c in range(len(cascades)):
    
    # Obtain the timing of the nodes that have fired
    idx = np.where(cascades[c] != -1)[0] # used nodes

    # Sort each cascade by earliest firing and keep the index order
    fired_nodes = [cascades[c,i] for i in idx]
    val = np.sort(fired_nodes)
    order = np.argsort(fired_nodes)

    if c != 0 and (c > x*1000):
        print(x * 1000)
        x = x + 1

    # For all used nodes
    # Don't take the first value (it's value is 0, it belongs to the
    # stimulated node)
    for i in range(1,len(val)):
        
        # num_cascades stores the amount of times each node has generated a cascade
        # num_cascades = [np.bincount(cascades.T[k].astype(int)+1)[1] for k in range(cascades.shape[1])]
        num_cascades[idx[order[i]]] = num_cascades[idx[order[i]]] + 1

        for j in range(i-1):
            
            if diffusion_type == 'exp':
                A_potential[idx[order[j]], idx[order[i]]] = A_potential[idx[order[j]], idx[order[i]]] + val[i] - val[j]

            if (diffusion_type == 'pl') and (val[i] - val[j] > 1):
                A_potential[idx[order[j]], idx[order[i]]] = A_potential[idx[order[j]], idx[order[i]]] + np.log(val[i] - val[j])
                
            if diffusion_type == 'rayleigh':
                A_potential[idx[order[j]], idx[order[i]]] = A_potential[idx[order[j]], idx[order[i]]] + 0.5 * (val[i] - val[j])**2;


    for j in range(N):
        
        # If the node has spiked
        if np.where(idx==j)[0].shape[0] == 0:

            for i in range(len(val)):
                
                if diffusion_type == 'exp':
                    A_bad[idx[order[i]], j] = A_bad[idx[order[i]], j] + (horizon - val[i])
                if (diffusion_type == 'pl') and (horizon - val[i] > 1):
                    A_bad[idx[order[i]], j] = A_bad[idx[order[i]], j] + np.log(horizon - val[i])
                if diffusion_type == 'rayleigh':
                    A_bad[idx[order[i]], j] = A_bad[idx[order[i]], j] + 0.5*(horizon-val[i])**2;
            
        
try: 
    foldername = "r/CRCNS_" + str(d) + "/"
    np.savetxt(foldername + "a_potential_" + cascadeOption  + ".csv", A_potential, delimiter=",")
    np.savetxt(foldername + "a_bad.csv_" + cascadeOption  + ".csv", A_bad, delimiter=",")
    np.savetxt(foldername + "cascades_" + cascadeOption  + ".csv", cascades, delimiter=",")
    np.savetxt(foldername + "num_cascades_" + cascadeOption  + ".csv", num_cascades, delimiter=",")

except Exception as e:
    print(e)


print('Finished generating cascades')

os.system('poweroff')






