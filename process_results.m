function process_results(sparsity, r, diffusion_type, m, fileToTrackProgress)

r = 'temporary/accuracy.csv';
S = csvread('w/S_matrix.csv');
cascades = csvread('w/cascades.csv');
size_S = size(S);
num_nodes = size_S(2);


% Obtain each of the columns of the estimated adjacency matrix
for n = 1:num_nodes
	S_hat(:,n) = csvread(strcat('temporary/a_hat_',int2str(n), '.csv'));
end

% threshold based on defined level of sparsity
S_hat=pranav_threshold_sparsity(S_hat, sparsity);

% file handle for writing results
resultsFileHandle=fopen(r,'a');

% obtain the metrics
pranav_get_metrics(S,S_hat,diffusion_type,resultsFileHandle, cascades);

% close the File
fclose(resultsFileHandle);

% obtain estimated adjacency matrix
S_hat_adjacency=digraph(S_hat);

% write information to file
writetable(S_hat_adjacency.Edges, m);