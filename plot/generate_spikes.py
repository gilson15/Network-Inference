
print('Running Brian Simulator...')

import sys
import numpy
import os.path
# from matplotlib import pyplot as plt
from brian2  import *
# from utility import *

# # extract command line arguments
seed=int(sys.argv[1])
N=int(sys.argv[2])
I_var=float(sys.argv[3])
simulation_duration=int(sys.argv[4])*1000
stimulus=str(sys.argv[5])
sparsity=float(0.1)

networkFileName = 'spike_data/network_' + str(int(N)) + '_' + str(int(I_var*10)) + '_' + str(int(simulation_duration)) + '_' + stimulus +  '_' + str(seed) + '.csv'
firingsFileName = 'spike_data/firings_' + str(int(N)) + '_' + str(int(I_var*10)) + '_' + str(int(simulation_duration)) + '_' + stimulus +  '_' + str(seed) + '.csv'
indicesFileName = 'spike_data/indices_' + str(int(N)) + '_' + str(int(I_var*10)) + '_' + str(int(simulation_duration)) +  '_' + stimulus + '_' + str(seed) + '.csv'


if (os.path.isfile(networkFileName) and os.path.isfile(firingsFileName) and os.path.isfile(indicesFileName)):
    sys.exit('Files for Brian simulation found')
        

# set the default seed
devices.device.seed(seed)

# suppress warnings
BrianLogger.suppress_hierarchy('brian2.codegen')

firings=[]
indices=[]

tau=1*ms

if stimulus == 'normal':
    eqs= '''
    dv/dt = (0.04*v*v + 5*v + 140 - u + I)/tau : 1
    du/dt = (a*(b*v-u))/tau : 1
    '''
    eqs = eqs + '\nI = ' + str(I_var) + '*randn() : 1 (constant over dt)' + '''
    a:1
    b:1
    c:1
    d:1
    '''
    threshold='v>30'

    reset='''
    v=c
    u=u+d
    '''

    # Initialise the Neuron Group and set the Parameters
    G = NeuronGroup(N,eqs,threshold=threshold,reset=reset,method='euler')
    M = StateMonitor(G, 'v', record=0)
    G.a = 0.02
    G.b = 0.2
    G.c = '-65+15*rand()**2'
    G.d = '8-6*rand()**2'

    # Define the connection values and the conditions
    S = Synapses(G, G, 'w:1', on_pre='v_post += w')
    S.connect(condition='i!=j', p=sparsity)
    S.w='30*rand()'

    # reset v and u values
    G.v=-65
    G.u=G.b*G.v


    spikemon = SpikeMonitor(G)

    run(simulation_duration*ms)

if stimulus == 'abs':
    eqs= '''
    dv/dt = (0.04*v*v + 5*v + 140 - u + I + stimulation)/tau : 1
    du/dt = (a*(b*v-u))/tau : 1
    I = 0*randn() : 1 (constant over dt)
    a:1
    b:1
    c:1
    d:1
    stimulation:1
    '''

    threshold='v>30'

    reset='''
    v=c
    u=u+d
    '''

    # Initialise the Neuron Group and set the Parameters
    G = NeuronGroup(N,eqs,threshold=threshold,reset=reset,method='euler')
    M = StateMonitor(G, 'v', record=0)
    G.a = 0.02
    G.b = 0.2
    G.c = '-65+15*rand()**2'
    G.d = '8-6*rand()**2'

    # Define the connection values and the conditions
    S = Synapses(G, G, 'w:1', on_pre='v_post += w')
    S.connect(condition='i!=j', p=sparsity)
    S.w='30*rand()'

    # reset v and u values
    # G.v=-65
    # G.u=G.b*G.v

    time = 0
    # run the stimulation N number of times
    # at each iteration, stimulate a different node
    while time < simulation_duration:
        
        # Select a random neuron from the system to stimulate
        stimulated_node = int(round((N-1)*np.random.rand(1)[0]))

        # Select a random amount of time to stimulate the neuron
        stimulation_duration = int(round(200*np.random.rand(1)[0]))

        # Beware of the difference between simulation and sTimulation
        if time + stimulation_duration > simulation_duration:
            stimulation_duration = simulation_duration - time

        time = time + stimulation_duration

        # only stimulate 1 node with the absolute value of a normal distribution
        G.stimulation = 0
        G.stimulation[stimulated_node] = I_var*abs(np.random.randn(1)[0])

        spikemon = SpikeMonitor(G)

        run(stimulation_duration*ms)

        # store firings and indices
        firings.append(list(spikemon.t/ms))
        indices.append(list(spikemon.i))
# plot(M.t/ms, M.v[0])
# # for t in spikemon.t:
# #     axvline(t/ms, ls='--', c='blue', lw=3)
# # axhline(0.8, ls=':', c='blue', lw=3)
# xlabel('Time (ms)')
# ylabel('Membrane potential (mv)')
# grid()
# title('Fast Spiking neuron')
# print("Spike times: %s" % spikemon.t[:])
# show()


# Write Network to File
myNetworkFile=open(networkFileName,'w')
for l in zip(S.i, S.j, S.w):
        myNetworkFile.write(",".join(map(str,l)))
        myNetworkFile.write("\n")
myNetworkFile.close()

# Write Firings to File
myFiringsFile=open(firingsFileName,'w')
for l in firings:
        myFiringsFile.write(",".join(map(str,l)))
        myFiringsFile.write("\n")
myFiringsFile.close()

# Write Indices to File
myIndicesFile=open(indicesFileName,'w')
for l in indices:
        myIndicesFile.write(",".join(map(str,l)))
        myIndicesFile.write("\n")
myIndicesFile.close()


