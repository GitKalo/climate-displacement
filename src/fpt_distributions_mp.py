"""
Calculate first-passage-time distributions in via multiprocessing parallelism.
"""

import json
import os
import time
from itertools import permutations
from multiprocessing import Pool, cpu_count

import numpy as np
import pandas as pd
import networkx as nx

def fpt_distribution(i, j, T, stop=1e-10, max_steps=100000):
    """
    Calculate a first-passage-time distribution using matrix-vector products.

    Uses the "taboo matrix" approach and avoids full matrix powers.
    """
    T = np.asarray(T, dtype=float)
    if T.ndim != 2 or T.shape[0] != T.shape[1]:
        raise ValueError("T must be a square matrix.")
    n_states = T.shape[0]
    if not 0 <= i < n_states or not 0 <= j < n_states:
        raise ValueError("i and j must be valid state indices.")
    if stop < 0:
        raise ValueError("stop must be non-negative.")
    if max_steps < 1:
        raise ValueError("max_steps must be positive.")

    non_target = np.arange(n_states) != j
    target_column = T[non_target, j]
    transitions_without_target = T[np.ix_(non_target, non_target)]

    if i == j:
        state = T[j, non_target].copy()
        first_passage = float(T[j, j])
    else:
        state = np.zeros(n_states - 1)
        state[i if i < j else i - 1] = 1.0
        first_passage = float(state @ target_column)    # Actually just target_column, because state all 1s?

    fpt = [first_passage]
    while state.sum() > stop:
        if len(fpt) >= max_steps:
            raise RuntimeError(
                f"FPT calculation for ({i}, {j}) exceeded max_steps={max_steps}."
            )
        state = state @ transitions_without_target
        fpt.append(float(state @ target_column))

    total = sum(fpt)
    if total == 0:
        raise ValueError(f"State {j} is unreachable from state {i}.")
    fpt = [x / total for x in fpt]
    
    # print(f"Calculated FPT distribution for pair ({i}, {j}) with {len(fpt)} steps.")
    return (i, j), fpt

def run_parallel(transition_matrix, pairs, stop=1e-10, n_workers=None, callback=None):
    """
    Run FPT distributions asynchronously with one callback per result.
    """
    if n_workers is None:
        n_workers = cpu_count()

    with Pool(processes=n_workers) as pool:
        async_results = [
            pool.apply_async(
                fpt_distribution,
                args=(source, target, transition_matrix, stop),
                callback=callback,
            )
            for source, target in pairs
        ]

        pool.close()    # Signal no more submissions

        # Wait for each result so processing happens as workers finish tasks
        # and so that worker and callback exceptions are surfaced
        for async_result in async_results:
            async_result.get()

        pool.join()     # Cleanup (not super necessary given AsyncResult.get() above)


def append_result_jsonl(file, result):
    """
    Append one completed FPT result to an open JSONL file.
    """
    (i, j), fpt_probs = result
    record = {
        "source": i,
        "target": j,
        "fpt_probs": fpt_probs,
    }
    file.write(json.dumps(record) + "\n")
    file.flush()

if __name__ == "__main__":
    ### Construct geographical network transition matrix
    # TODO: Maybe could construct transition matrix directly from CSV file. 
    # Although this way it could be easier to extend to other edge properties in the future.
    geographical_neighbours = pd.read_csv('data/geographical_neighbours.csv')
    G_geo = nx.from_pandas_edgelist(
        geographical_neighbours,
        source='focal',
        target='neighbour',
        edge_attr=['road_connected', 'src_vx', 'tgt_vx', 'src_distance', 'tgt_distance', 'in_distance', 'road_distance'],
        create_using=nx.Graph()
    )
    transition_matrix = nx.to_numpy_array(G_geo, nodelist=sorted(G_geo.nodes()))    # Adjacency matrix
    transition_matrix /= np.sum(transition_matrix, axis=1, keepdims=True)   # Normalize to obtain transition matrix
        
    # pairs = [(0,10), (12,20), (25,35)]  # Example pairs; replace with actual pairs.
    pairs = list(permutations(range(transition_matrix.shape[0]), 2))

    start_time = time.perf_counter()
    output_filepath = "fpt_results.jsonl"
    if os.path.exists(output_filepath):
        print(f"Output file {output_filepath} already exists. It will be overwritten.")

    with open(output_filepath, "w") as output_file:
        completed = [0]     # This is a list so that it's mutable and avoids some scoping issues downstream

        def write_result(result):
            append_result_jsonl(output_file, result)
            completed[0] += 1
            source, target = result[0]
            print(
                f"Wrote pair {completed[0]}/{len(pairs)}: ({source}, {target}) with {len(result[1])} steps.",
                flush=True,
            )

        print(f"Starting {len(pairs)} distributions...", flush=True)
        run_parallel(
            transition_matrix=transition_matrix,
            pairs=pairs,
            stop=5e-1,
            n_workers=4,
            callback=write_result,
        )

    elapsed_time = time.perf_counter() - start_time
    print(f"Calculated and saved {len(pairs)} distributions.")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")