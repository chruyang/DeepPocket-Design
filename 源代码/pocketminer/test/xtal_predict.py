import tensorflow as tf
from models import MQAModel
import numpy as np
from glob import glob
import mdtraj as md
import os

from validate_performance_on_xtals import process_strucs, predict_on_xtals
from extract_residue import extract_residue_ids_from_pdb

def make_predictions(pdb_paths, model, nn_path, debug=False, output_basename=None):
    '''
        pdb_paths : list of pdb paths
        model : MQAModel corresponding to network in nn_path
        nn_path : path to checkpoint files
    '''
    strucs = [md.load(s) for s in pdb_paths]
    X, S, mask = process_strucs(strucs)
    if debug:
        np.save(f'{output_basename}_X.npy', X)
        np.save(f'{output_basename}_S.npy', S)
        np.save(f'{output_basename}_mask.npy', mask)
    predictions = predict_on_xtals(model, nn_path, X, S, mask)
    return predictions

# main method
if __name__ == '__main__':
    # TO DO - provide input pdb(s), output name, and output folder
    strucs = [
        '../data/input.pdb',
    ]
    output_name = 'output'
    output_folder = '.'

    # debugging mode can be turned on to output protein features and sequence
    debug = False

    # Load MQA Model used for selected NN network
    nn_path = "../models/pocketminer"
    DROPOUT_RATE = 0.1
    NUM_LAYERS = 4
    HIDDEN_DIM = 100
    model = MQAModel(node_features=(8, 50), edge_features=(1, 32),
                     hidden_dim=(16, HIDDEN_DIM),
                     num_layers=NUM_LAYERS, dropout=DROPOUT_RATE)
    
    
    if debug:
        output_basename = f'{output_folder}/{output_name}'
        predictions = make_predictions(strucs, model, nn_path, debug=True, output_basename=output_basename)
    else:
        predictions = make_predictions(strucs, model, nn_path)

    # output filename can be modified here


    # 残基 id
    residue_ids = extract_residue_ids_from_pdb("../data/input.pdb")
    np.savetxt(os.path.join(output_folder,f'{output_name}.txt'), predictions, fmt='%.2f', delimiter='\n')

    # 读取文本文件
    with open("../test/output.txt", "r") as file:
        lines = file.readlines()

    # 读取原始 PDB 文件
    with open("../data/input.pdb", "r") as pdb_file:
        pdb_lines = pdb_file.readlines()

    # 遍历原始 PDB 文件的每一行
    output_lines = []
    for pdb_line in pdb_lines:
        if pdb_line.startswith("ATOM"):
            # 获取行的索引，假设它是当前 PDB 文件行的第6个切片值
            line_index = int(pdb_line[22:26])
            # 获取第63到66列的值
            columns_to_replace = pdb_line[62:66]
            # 替换为文本文件的每一行值
            new_value = lines[line_index - 1].strip()  # 获取文本文件中对应行的值
            new_line = pdb_line[:62] + new_value + pdb_line[66:]
            output_lines.append(new_line)
        else:
            output_lines.append(pdb_line)

    # 写入新的 PDB 文件
    with open("../data/output.pdb", "w") as output_pdb_file:
        output_pdb_file.writelines(output_lines)

    count = [0, 0, 0, 0] # 统计个数
    # 打开文件以进行读写
    with open("../test/output.txt", "r+") as file:
        # 读取文件内容
        lines = file.readlines()
        # 将文件指针移到文件开头
        file.seek(0)
        # 遍历每一行内容，并插入残基ID
        for residue_id, line in zip(residue_ids, lines):
            # 根据值进行计数
            if float(line) < 0.25:
                count[0] += 1
            elif float(line) < 0.50:
                count[1] += 1
            elif float(line) < 0.75:
                count[2] += 1
            else:
                count[3] += 1
            residue_id = f"{residue_id: <20}"  # 将残基ID格式化为最多占10个空格的形式
            file.write(f"{residue_id} {line}")
