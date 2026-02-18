import sys
import os
import torch
import numpy as np
import warnings
import traceback

# BioPython 用于坐标提取
from Bio.PDB import PDBParser
from Bio.PDB.PDBExceptions import PDBConstructionWarning

try:
    import md_engine
    HAS_MD = True
except ImportError:
    print("[Warning] md_engine.py not found or OpenMM missing. Skipping MD.")
    HAS_MD = False

# ==========================================
# 1. 路径配置 (请根据您的实际路径修改)
# ==========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# PocketMiner 源码路径 (包含 xtal_predict.py 的那个 src 文件夹)
# 假设结构是: pockettomol/gvp-pocket_pred/gvp-pocket_pred/src/
PM_SOURCE_DIR = os.path.join(CURRENT_DIR, 'gvp-pocket_pred/gvp-pocket_pred/src')

# PocketMiner 权重路径
# 警告：这里必须指向包含 checkpoint 文件的具体文件夹，或者是权重文件的前缀
# 根据您之前的反馈，权重可能在 "源代码/pocketminer/models"
# 请确保这里填写的路径是正确的！
PM_MODEL_WEIGHTS_DIR = "/root/autodl-tmp/pocket/pockettomol/gvp-pocket_pred/gvp-pocket_pred/models"

# GraphBP 源码路径
GBP_SOURCE_DIR = os.path.join(CURRENT_DIR, 'GraphBP/GraphBP')
GBP_MODEL_WEIGHT = os.path.join(GBP_SOURCE_DIR, 'trained_model/model_33.pth')

# 将源码目录加入系统路径
sys.path.append(PM_SOURCE_DIR)
sys.path.append(GBP_SOURCE_DIR)

# ==========================================
# 2. 导入模型模块
# ==========================================
print("Importing modules...")
try:
    # 导入 PocketMiner 组件
    # 必须导入 models.py 和 xtal_predict.py 中用到的库
    import mdtraj as md
    from models import MQAModel

    # 尝试从 xtal_predict 导入 make_predictions
    # 如果 xtal_predict.py 在 src 下，直接 import 应该没问题
    try:
        from xtal_predict import make_predictions
    except ImportError:
        # 如果直接导入失败，尝试手动加载 (这是为了应对奇怪的目录结构)
        import importlib.util

        spec = importlib.util.spec_from_file_location("xtal_predict", os.path.join(PM_SOURCE_DIR, "xtal_predict.py"))
        xtal_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(xtal_module)
        make_predictions = xtal_module.make_predictions

    print("[Success] PocketMiner modules imported.")
except ImportError as e:
    print(f"[Error] Failed to import PocketMiner: {e}")
    # PocketMiner 强依赖 tensorflow 和 mdtraj

try:
    # 导入 GraphBP 组件
    from runner import Runner
    from config import conf

    print("[Success] GraphBP modules imported.")
except ImportError as e:
    print(f"[Error] Failed to import GraphBP: {e}")


# ==========================================
# 3. 核心逻辑
# ==========================================

def get_residue_center_from_pdb(pdb_path, residue_index_0_based):
    """将 残基索引 -> 空间坐标"""
    parser = PDBParser(QUIET=True)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', PDBConstructionWarning)
        structure = parser.get_structure('target', pdb_path)

    atoms_coords = []
    current_idx = 0
    found = False

    # 严格按照 PDB 解析顺序遍历 (Chain -> Residue)
    for model in structure:
        for chain in model:
            for residue in chain:
                # 排除杂项 (如水分子)
                if residue.id[0] != ' ':
                    continue

                if current_idx == residue_index_0_based:
                    for atom in residue:
                        if atom.element != 'H':
                            atoms_coords.append(atom.coord)
                    found = True
                    break
                current_idx += 1
            if found: break
        if found: break

    if not found or len(atoms_coords) == 0:
        raise ValueError(f"Residue index {residue_index_0_based} invalid for {pdb_path}")

    center = np.mean(atoms_coords, axis=0)
    return torch.tensor(center, dtype=torch.float32)


def run_pocketminer_logic(pdb_path):
    """
    [实战版] 运行 PocketMiner 真实预测
    """
    print(f"\n--- Step 1: PocketMiner Analysis on {os.path.basename(pdb_path)} ---")

    # 1. 定义模型 (参数必须与训练时一致)
    print("Initializing Model (Features: 8/50/1/32, Hidden: 100)...")
    model = MQAModel(
        node_features=(8, 50),
        edge_features=(1, 32),
        hidden_dim=(16, 100),
        num_layers=4,
        dropout=0.1
    )

    # 2. 检查权重文件是否存在
    # PocketMiner 的 predict_on_xtals 函数会直接用 tf.train.Checkpoint(model=model).restore(nn_path)
    # 所以传入的必须是 checkpoint 的"前缀"或者包含 checkpoint 文件的"目录"

    # 策略：如果目录里有 "checkpoint" 文件，直接传目录；
    # 如果只有 .index 文件，传具体的文件路径前缀
    checkpoint_index = os.path.join(PM_MODEL_WEIGHTS_DIR, "best_task1_gvp_fold0.index")

    if os.path.exists(checkpoint_index):
        # 构造前缀路径: .../best_task1_gvp_fold0
        nn_path = os.path.join(PM_MODEL_WEIGHTS_DIR, "best_task1_gvp_fold0")
        print(f"Using weights: {nn_path}")
    elif os.path.exists(os.path.join(PM_MODEL_WEIGHTS_DIR, "checkpoint")):
        nn_path = PM_MODEL_WEIGHTS_DIR
        print(f"Using checkpoint dir: {nn_path}")
    else:
        print(f"[Error] Weights not found in {PM_MODEL_WEIGHTS_DIR}")
        return None

    # 3. 运行预测
    print("Running inference...")
    try:
        # xtal_predict.make_predictions 接收的是 [pdb_path] 列表
        predictions = make_predictions([pdb_path], model, nn_path)

        # 提取结果
        # predictions 可能是一个列表的列表，或者 numpy 数组
        if isinstance(predictions, list):
            probs = np.array(predictions[0])
        else:
            probs = np.array(predictions)
            if len(probs.shape) > 1 and probs.shape[0] == 1:
                probs = probs[0]

        # 找到最大值索引
        best_residue_idx = np.argmax(probs)
        max_prob = probs[best_residue_idx]

        print(f"Prediction Success! (Top residue: {best_residue_idx}, Prob: {max_prob:.4f})")
        return best_residue_idx

    except Exception as e:
        print(f"[Error] Inference failed: {e}")
        traceback.print_exc()
        return None


def run_graphbp_logic(pdb_path, center_coords, output_dir):
    """运行 GraphBP 生成"""
    print(f"\n--- Step 2: GraphBP Generation at {center_coords.numpy()} ---")

    # 强制使用 GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    conf['model']['use_gpu'] = (device == 'cuda')
    conf['device'] = device

    runner = Runner(conf)

    # 加载权重
    if not os.path.exists(GBP_MODEL_WEIGHT):
        print(f"[Error] GraphBP weights not found at {GBP_MODEL_WEIGHT}")
        return

    state_dict = torch.load(GBP_MODEL_WEIGHT, map_location=device)
    runner.model.load_state_dict(state_dict)
    runner.model.to(device)

    # 生成
    try:
        mols_dict = runner.generate_direct(
            pdb_path=pdb_path,
            target_center=center_coords,
            num_gen=10,
            temperature=[1.0, 1.0, 1.0, 1.0],
            min_atoms=10, max_atoms=40,
            binding_site_range=15.0
        )

        if mols_dict:
            import pickle
            res_path = os.path.join(output_dir, 'generated_molecules.pkl')
            with open(res_path, 'wb') as f:
                pickle.dump(mols_dict, f)
            print(f"Success! Result saved to {res_path}")

    except Exception as e:
        print(f"[Error] Generation failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    TARGET_PDB = os.path.join(CURRENT_DIR, "../源代码/pocketminer/data/input.pdb")
    OUTPUT_DIR = os.path.join(CURRENT_DIR, "output_results")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if os.path.exists(TARGET_PDB):
        # Step 1: 预测位置 (PocketMiner)
        target_res_idx = run_pocketminer_logic(TARGET_PDB)

        if target_res_idx is not None:

            # Step 1.5: 运行 MD 模拟 (新增步骤)
            # 默认使用原始 PDB，如果 MD 成功则替换为 MD 后的 PDB
            pdb_for_graphbp = TARGET_PDB

            if HAS_MD:
                try:
                    # 运行 MD，让口袋张开
                    print("\n=== Step 1.5: Relaxing Structure with Molecular Dynamics ===")
                    open_pdb_path = md_engine.run_simulation_and_pick_open_structure(
                        pdb_path=TARGET_PDB,
                        target_residue_idx=target_res_idx,
                        output_dir=OUTPUT_DIR,
                        steps=10000  # 测试用1万步，正式用可加到10万+
                    )
                    # 将 GraphBP 的输入替换为张开后的结构
                    pdb_for_graphbp = open_pdb_path
                except Exception as e:
                    print(f"[MD Error] Simulation failed: {e}. Falling back to static PDB.")

            # Step 2: 转换坐标 (使用最终选定的 PDB)
            # 注意：MD 后的 PDB 坐标变了，必须重新计算中心！
            center = get_residue_center_from_pdb(pdb_for_graphbp, target_res_idx)

            # Step 3: 生成分子 (GraphBP)
            run_graphbp_logic(pdb_for_graphbp, center, OUTPUT_DIR)

        else:
            print("PocketMiner failed.")
    else:
        print(f"Input PDB not found: {TARGET_PDB}")