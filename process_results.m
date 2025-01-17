function process_results(N, sparsity, r, networkFileName, diffusion_type, m, fileToTrackProgress)

cascades = csvread('w/cascades.csv');
% network = csvread(networkFileName);
%
% % obtain adjacency matrix
% S=zeros(int32(N),int32(N));
% for i=1:size(network,1)
%     S(network(i,1)+1,network(i,2)+1)=network(i,3);
% end

% Obtain each of the columns of the estimated adjacency matrix
for n = 1:N
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
