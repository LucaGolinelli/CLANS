import numpy as np
import numba
import clans.config as cfg


def calculate_attraction_values():
    # Pairs, which have the init value of 100 (no HSP), automatically get the value of 0
    minus_log_similarity_values = np.where(cfg.similarity_values_mtx > 1, 0, -np.log10(cfg.similarity_values_mtx))
    max_value = np.amax(minus_log_similarity_values)
    cfg.attraction_values_mtx = np.true_divide(minus_log_similarity_values, max_value)

    #print("Attraction values:\n" + str(cfg.attraction_values_mtx))


def define_connected_sequences(mode):
    # Create the 2D redundant boolean matrix of connections
    if mode == 'hsp':
        cfg.connected_sequences_mtx = np.where(cfg.similarity_values_mtx <= cfg.run_params['similarity_cutoff'], 1, 0)
    elif mode == 'att':
        cfg.connected_sequences_mtx = np.where(cfg.attraction_values_mtx >= cfg.run_params['similarity_cutoff'], 1, 0)
    #print("Connected_sequences:\n" + str(cfg.connected_sequences))


# Create a list of connected pairs (non-redundant, [indexi][indexj]) for the line plot graphics
@numba.njit
def create_lists(connected_sequences_mtx, attraction_values_mtx):
    total_seq_num = connected_sequences_mtx.shape[0]
    hsp_num = 0
    connections_list = []
    att_values_list = []

    for i in range(total_seq_num - 1):
        for j in range(i + 1, total_seq_num):
            if i < j and connected_sequences_mtx[i][j] == 1:
                connected_pair_tuple = (i, j)
                connections_list.append(connected_pair_tuple)
                att_values_list.append(attraction_values_mtx[i][j])
                hsp_num += 1

    return hsp_num, connections_list, att_values_list


def define_connected_sequences_list():

    hsp_num, connections_list, att_values_list = create_lists(cfg.connected_sequences_mtx, cfg.attraction_values_mtx)

    cfg.connected_sequences_list = np.array(connections_list, dtype=int)
    cfg.att_values_for_connected_list = np.array(att_values_list, dtype=float)
    cfg.run_params['connections_num'] = hsp_num

    if cfg.run_params['type_of_values'] == 'hsp':
        print("Number of connections (under the P-value of " + str(cfg.run_params['similarity_cutoff']) + "): "
              + str(hsp_num))
    else:
        print("Number of connections (above the threshold of " + str(cfg.run_params['similarity_cutoff']) + "): "
              + str(hsp_num))

# Create a list of connected pairs (non-redundant, [indexi][indexj]) for the line plot graphics
@numba.njit
def create_lists_subset(connected_sequences_mtx, attraction_values_mtx, in_subset_array):
    total_seq_num = connected_sequences_mtx.shape[0]
    hsp_num = 0
    connections_list = []
    att_values_list = []

    i_in_subset = 0
    for i in range(total_seq_num - 1):
        # sequence i is in the subset
        if in_subset_array[i]:
            j_in_subset = i_in_subset + 1
            for j in range(i + 1, total_seq_num):
                # sequence j is in the subset
                if in_subset_array[j]:
                    # If the sequences are connected and j is also in the subset, add the connection to the list
                    if connected_sequences_mtx[i][j] == 1:
                        # Adding the sequences indices in the subset to the list of connected pairs
                        connected_pair_tuple = (i_in_subset, j_in_subset)
                        connections_list.append(connected_pair_tuple)
                        att_values_list.append(attraction_values_mtx[i][j])
                        hsp_num += 1
                    j_in_subset += 1
            i_in_subset += 1

    return hsp_num, connections_list, att_values_list


def define_connected_sequences_list_subset():

    hsp_num, connections_list, att_values_list = create_lists_subset(cfg.connected_sequences_mtx,
                                                                     cfg.attraction_values_mtx,
                                                                     cfg.sequences_array['in_subset'])

    cfg.connected_sequences_list_subset = np.array(connections_list, dtype=int)
    cfg.att_values_for_connected_list_subset = np.array(att_values_list, dtype=float)

    if cfg.run_params['type_of_values'] == 'hsp':
        print("Number of connections in the subset (under the P-value of " + str(cfg.run_params['similarity_cutoff'])
              + "): " + str(hsp_num))
    else:
        print("Number of connections in the subset (above the threshold of " + str(cfg.run_params['similarity_cutoff'])
              + "): " + str(hsp_num))

