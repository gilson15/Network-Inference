
function parallel_cvx(i, num_nodes, num_processors, horizon, type_diffusion, cascadesFileName, aBadFileName, aPotentialFileName, numCascadesFileName, aHatFileName, numFiringsFileName)

A_potential = csvread(aPotentialFileName);
A_bad = csvread(aBadFileName);
cascades = csvread(cascadesFileName);
num_cascades = csvread(numCascadesFileName);
num_firings = csvread(numFiringsFileName);
% run('cvx_setup.m');
% Number of nodes that each processor will compute
% Matlab rounds integers by default
% Use fix() to truncate 
nodes_processor = int8(fix(num_nodes/num_processors));
remaining_nodes = mod(num_nodes, num_processors);

%
% MATLAB starts indexing from 1
nodes = i + 1;
fprintf('Nodes to be computed are: ');
fprintf('%i ', nodes);
fprintf('\n');
total_obj = 0;
for n = nodes
	fprintf('Computing node %i \n ', n);
	if (num_firings(n)==0)
		a_hat = zeros(num_nodes,1);
		filename = aHatFileName + string(n) + '.csv';
		csvwrite(filename, full(a_hat)); 
		continue;
	end

	tic
	% Inside solve_using_cvx, num_firings turns into num_cascades, don't want to change the code
	[a_hat, obj] = solve_using_cvx(n, type_diffusion, num_nodes, num_firings, A_potential, A_bad, cascades);
	stop=toc;

	total_obj = total_obj + obj;
	filename = aHatFileName + string(n) + '.csv';
	csvwrite(filename, full(a_hat)); 
	disp(strcat('Finished computing node ', string(n)))
end

