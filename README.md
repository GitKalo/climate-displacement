# Scenario-driven analysis of climate-induced displacement [working title]

Data analysis and implementation of the random walk methodology for the paper "...".

Follow-up from Comlpexity72h preprint:
- Carranza, D., Sharma, D., Malveiro, F., Kohlrausch, G., John, J.M., Danovski, K., Bozhidarova, M., Zheng, R., Sousa, S. (2025). [Walking Through Complex Spatial Patterns of Climate and Conflict-Induced Displacements.](https://arxiv.org/abs/2506.22120) arXiv preprint arXiv:2506.22120.

## Repo structure

Overview of files and folders:
- All data manipulation and simulation **scripts** are under `src/`.
    - The main simulation script is `rw_targeted_mp.py`, for generating walks from each source to each target on the network. Whether paths are biased by IDP-weighted transition probabilities or are instead uniform is controlled by a command-line input to the script.
    - The `extract_hazard_exposure_vectors.py` script calculates the distribution of IDPs over hazard types that left each settlement, saving to the `data/settlement_IDPs.txt` file (see script docstring for details).
    - The `path_hazards.py` script describes a procedure for calculating hazards along paths.
    - The postprocessing scripts `reduce_paths.py` and `paths_to_counts.py` are used for reducing the size of the targeted data scripts. A usual workflow will follow `rw_targeted_mp.py` --> `reduce_paths.py` --> `paths_to_counts.py`.
    - The `network_utils.py` defines functions shared between scripts.
- All **data** used by scripts is under `data/`.
    - `hazards_displacements.csv` is a cleaner subset of the data used to analyze the hazard distributions for settlements and paths.
- All notebooks for data **analysis and visualization** are under the main directory, e.g.:
    - `walk_statistics.ipynb` — Summary statistics for random walks on entire network.
    - `hazard_plot.ipynb` — Plot hazard distributions.

Note that scripts and notebook often save to folders `out/` and `figs/`, which are created on-the-go locally and ignored by version control.