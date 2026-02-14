import sys
import os
import torch
import numpy as np
import warnings
from Bio.PDB import PDBParser
from Bio.PDB.PDBExceptions import PDBConstructionWarning

# ==========================================
# 1. 路径配置 (根据您上传的文件结构)
# ==========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# PocketMiner 源码路径
PM_SOURCE_DIR = os.path.join(CURRENT_DIR, 'gvp-pocket_pred/gvp-pocket_pred/src')
PM_MODEL_WEIGHTS = os.path.join(CURRENT_DIR, 'gvp-pocket_pred/gvp-pocket_pred/models/pocketminer')

# GraphBP 源码路径
GBP_SOURCE_DIR = os.path.join(CURRENT_DIR, 'GraphBP/GraphBP')
GBP_MODEL_WEIGHT = os.path.join(GBP_SOURCE_DIR, 'trained_model/model_33.pth')

# 将源码目录加入系统路径，以便 import
sys.path.append(PM_SOURCE_DIR)
sys.path.append(GBP_SOURCE_DIR)

# ==========================================
# 2. 导入模型模块
# ==========================================
try:
    # 导入 PocketMiner 组件
    # 注意：根据 xtal_predict.py 的逻辑，我们需要构建图并运行模型
    # 这里我们简化逻辑，假设可以调用其内部处理函数
    # 如果实际运行困难，这部分通常需要 tensorflow/keras 环境
    from xtal_predict import make_predictions
    from models import MQAModel  # PocketMiner 的模型类

    print("[Success] PocketMiner modules imported.")
except ImportError as e:
    print(f"[Error] Failed to import PocketMiner: {e}")
    # 提示：PocketMiner 需要 tensorflow, biotite 等库

try:
    # 导入 GraphBP 组件
    from runner import Runner
    from config import conf

    print("[Success] GraphBP modules imported.")
except ImportError as e:
    print(f"[Error] Failed to import GraphBP: {e}")


# ==========================================
# 3. 核心桥梁逻辑 (Bridge Logic)
# ==========================================

def get_residue_center_from_pdb(pdb_path, residue_index_0_based):
    """
    桥梁函数核心：将 残基索引(Index) -> 空间坐标(Coordinates)
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure('target', pdb_path)

    atoms_coords = []
    current_idx = 0
    found = False

    # 遍历顺序必须与 PocketMiner 的图构建顺序严格一致
    # PocketMiner 通常按 Chain -> Residue 顺序遍历
    for model in structure:
        for chain in model:
            for residue in chain:
                # 排除杂项 (如水分子 HOH)
                if residue.id[0] != ' ':
                    continue

                if current_idx == residue_index_0_based:
                    # 找到目标残基，提取所有重原子
                    for atom in residue:
                        if atom.element != 'H':
                            atoms_coords.append(atom.coord)
                    found = True
                    break

                current_idx += 1
            if found: break
        if found: break

    if not found:
        raise ValueError(f"Residue index {residue_index_0_based} out of range for {pdb_path}")

    # 计算几何中心 (Centroid)
    center = np.mean(atoms_coords, axis=0)
    return torch.tensor(center, dtype=torch.float32)


def run_pocketminer_logic(pdb_path):
    """
    运行 PocketMiner 并返回概率最高的残基索引。
    """
    print(f"\n--- Step 1: PocketMiner Analysis on {os.path.basename(pdb_path)} ---")

    # 模拟 PocketMiner 的预测过程
    # 实际代码中，这里应该加载模型并运行 make_predictions
    # 由于环境配置复杂，这里展示逻辑框架：

    # 1. 加载模型 (伪代码，参考 xtal_predict.py)
    # model = MQAModel(...)
    # model.load_weights(PM_MODEL_WEIGHTS)

    # 2. 预测
    # probs = make_predictions([pdb_path], model)
    # predictions = probs[0] # 拿到第一个蛋白的预测结果 (数组)

    # [开发调试用] 假设我们已经拿到了预测结果
    # 假设第 42 号残基是隐性口袋的热点
    print("Running inference... (Simulation)")
    # 实际部署时，请替换为真实的 model.predict 调用
    # best_residue_idx = np.argmax(predictions)

    best_residue_idx = 42  # <--- 这是一个示例，代表模型认为第42个残基最重要
    max_prob = 0.95

    print(f"Prediction Done. Best Residue Index: {best_residue_idx} (Prob: {max_prob:.4f})")
    return best_residue_idx


def run_graphbp_logic(pdb_path, center_coords, output_dir):
    """
    运行 GraphBP 在指定中心生成分子
    """
    print(f"\n--- Step 2: GraphBP Generation at {center_coords.numpy()} ---")

    # 1. 配置与初始化
    # 强制使用 GPU 如果可用
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    conf['model']['use_gpu'] = (device == 'cuda')
    conf['device'] = device

    runner = Runner(conf)

    # 2. 加载权重
    if not os.path.exists(GBP_MODEL_WEIGHT):
        print(f"[Error] GraphBP weights not found at {GBP_MODEL_WEIGHT}")
        return

    # map_location 确保 CPU 也能加载 CUDA 训练的权重
    state_dict = torch.load(GBP_MODEL_WEIGHT, map_location=device)
    runner.model.load_state_dict(state_dict)
    runner.model.to(device)

    # 3. 调用 generate_direct (直接传递坐标)
    try:
        mols_dict = runner.generate_direct(
            pdb_path=pdb_path,
            target_center=center_coords,  # 核心衔接点
            num_gen=10,  # 生成数量
            temperature=[1.0, 1.0, 1.0, 1.0],
            min_atoms=10,
            max_atoms=40,
            binding_site_range=15.0  # 切割半径
        )

        # 4. 保存结果
        import pickle
        res_path = os.path.join(output_dir, 'generated_molecules.pkl')
        with open(res_path, 'wb') as f:
            pickle.dump(mols_dict, f)
        print(f"Success! Generated molecules saved to {res_path}")

    except KeyError as e:
        print(f"[Error] Atom type mismatch in PDB: {e}")
        print("Suggestion: Check if PDB contains unsupported elements (e.g., MSE, HEM).")


# ==========================================
# 4. 主执行流
# ==========================================
if __name__ == "__main__":
    # 示例输入文件
    # 假设在 pocketminer/data/ 下有个 input.pdb
    TARGET_PDB = os.path.join(CURRENT_DIR, "../源代码/pocketminer/data/input.pdb")
    OUTPUT_DIR = os.path.join(CURRENT_DIR, "output_results")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if os.path.exists(TARGET_PDB):
        # 1. 预测位置
        target_res_idx = run_pocketminer_logic(TARGET_PDB)

        # 2. 转换坐标 (Bridge)
        center = get_residue_center_from_pdb(TARGET_PDB, target_res_idx)

        # 3. 生成分子
        run_graphbp_logic(TARGET_PDB, center, OUTPUT_DIR)
    else:
        print(f"Input PDB not found: {TARGET_PDB}")