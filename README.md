# Scenario-driven analysis of climate-induced displacement [working title]

Data analysis and implementation of the random walk methodology for the paper "...".

Follow-up from Comlpexity72h preprint:
- Carranza, D., Sharma, D., Malveiro, F., Kohlrausch, G., John, J.M., Danovski, K., Bozhidarova, M., Zheng, R., Sousa, S. (2025). [Walking Through Complex Spatial Patterns of Climate and Conflict-Induced Displacements.](https://arxiv.org/abs/2506.22120) arXiv preprint arXiv:2506.22120.

## Repo structure

Overview of files and folders:
- All data manipulation and simulation scripts are under `src/`.
- All data used by scripts is under `data/`.

Notebooks and scripts for data analysis and visualization are under the main directory, e.g.:
- `walk_statistics.ipynb` — Summary statistics for random walks on entire network.
- `hazard_plot.ipynb` — Plot hazard distributions.

Note that scripts and notebook often save to folders `out/` and `figs/`, which are created on-the-go locally and ignored by the repo.