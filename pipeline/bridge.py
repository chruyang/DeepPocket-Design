import sys
import os
import torch
import numpy as np
import traceback
import logging

# BioPython
from Bio.PDB import PDBParser
from Bio.PDB.PDBExceptions import PDBConstructionWarning
import warnings

# Dynamic Path Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES_DIR = os.path.join(BASE_DIR, 'modules')
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Append paths for external modules
sys.path.append(os.path.join(MODULES_DIR, 'gvp-pocket_pred', 'gvp-pocket_pred', 'src'))
sys.path.append(os.path.join(MODULES_DIR, 'GraphBP', 'GraphBP'))

# Initialize Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from pipeline import md_engine

    HAS_MD = True
except ImportError:
    logger.warning("MD Engine not found or OpenMM missing. Skipping MD steps.")
    HAS_MD = False

# Import Models (Wrapped in try-except for robustness)
try:
    import mdtraj as md
    from models import MQAModel  # PocketMiner Model
    # Dynamic import for xtal_predict if needed, else assume it's in path
    from xtal_predict import make_predictions
except ImportError as e:
    logger.error(f"Failed to import PocketMiner dependencies: {e}")

try:
    from runner import Runner
    from config import conf as graphbp_conf
except ImportError as e:
    logger.error(f"Failed to import GraphBP dependencies: {e}")


def get_residue_center(pdb_path, target_res_idx):
    """
    Robustly extracts the center of mass of a target residue.
    Bypasses BioPython to absolutely avoid the 'A000' OpenMM hex numbering crash.
    """
    coords = []
    target_str = str(target_res_idx).strip()

    with open(pdb_path, 'r') as f:
        for line in f:
            # 只看原子坐标行
            if line.startswith("ATOM") or line.startswith("HETATM"):
                # PDB标准格式：第 23-26 列是残基编号
                res_seq = line[22:26].strip()

                # 如果是我们要找的靶点残基
                if res_seq == target_str:
                    try:
                        # PDB标准格式：坐标分别在 31-38, 39-46, 47-54 列
                        x = float(line[30:38])
                        y = float(line[38:46])
                        z = float(line[46:54])
                        coords.append([x, y, z])
                    except ValueError:
                        continue

    if not coords:
        raise ValueError(f"Target residue {target_res_idx} not found in {pdb_path}")

    # 计算几何中心点
    center = np.mean(coords, axis=0)

    # 返回 GraphBP 需要的 PyTorch Tensor 格式
    return torch.tensor(center, dtype=torch.float32)


def run_pocketminer(pdb_path, weights_dir=None):
    """Run PocketMiner to predict cryptic pockets."""
    logger.info(f"Step 1: Running PocketMiner on {os.path.basename(pdb_path)}")

    if weights_dir is None:
        weights_dir = os.path.join(MODULES_DIR, 'gvp-pocket_pred', 'gvp-pocket_pred', 'models', 'best_task1_gvp_fold0')

    # Initialize Model Architecture
    model = MQAModel(node_features=(8, 50), edge_features=(1, 32),
                     hidden_dim=(16, 100), num_layers=4, dropout=0.1)

    # Check weights
    if not os.path.exists(weights_dir + ".index") and not os.path.isdir(weights_dir):
        logger.error(f"Weights not found at {weights_dir}")
        return None

    try:
        predictions = make_predictions([pdb_path], model, weights_dir)

        # Handle Output format
        probs = np.array(predictions[0]) if isinstance(predictions, list) else np.array(predictions)
        if len(probs.shape) > 1 and probs.shape[0] == 1: probs = probs[0]

        best_residue = np.argmax(probs)
        logger.info(f"Prediction Success: Top residue {best_residue} (Prob: {probs[best_residue]:.4f})")
        return best_residue

    except Exception as e:
        logger.error(f"PocketMiner Inference failed: {e}")
        traceback.print_exc()
        return None


def run_graphbp(pdb_path, center, output_dir, weights_path=None):
    """Run GraphBP to generate precisely a fixed number of organic molecules at the target center."""
    logger.info(f"Step 3: Running GraphBP generation (Target: 10 pure organic molecules)")

    if weights_path is None:
        weights_path = os.path.join(MODULES_DIR, 'GraphBP', 'GraphBP', 'trained_model', 'model_33.pth')

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    graphbp_conf['model']['use_gpu'] = (device == 'cuda')
    graphbp_conf['device'] = device

    if not os.path.exists(weights_path):
        logger.error(f"GraphBP weights not found at {weights_path}")
        return

    runner = Runner(graphbp_conf)
    runner.model.load_state_dict(torch.load(weights_path, map_location=device))
    runner.model.to(device)

    try:
        target_valid_mols = 10  # 目标：固定生成 10 个
        # 允许的有机元素白名单 (C, N, O, F, P, S, Cl, Br, I)
        ALLOWED_ATOMS = {6, 7, 8, 9, 15, 16, 17, 35, 53}

        filtered_mols_dict = {}
        valid_count = 0
        max_attempts = 5  # 最大尝试次数，防止死循环
        attempts = 0

        # 只要纯有机分子数量没攒够 10 个，就继续生成
        while valid_count < target_valid_mols and attempts < max_attempts:
            attempts += 1
            # 每次多生成一些以提高命中率（比如缺 5 个，就生成 15 个）
            batch_gen = max(10, (target_valid_mols - valid_count) * 3)

            logger.info(f"Attempt {attempts}: Generating batch of {batch_gen} molecules...")

            mols_dict = runner.generate_direct(
                pdb_path=pdb_path,
                target_center=center,
                num_gen=batch_gen,
                temperature=[1.0] * 4,
                min_atoms=10, max_atoms=40,
                binding_site_range=15.0
            )

            # 在内存中立刻过滤刚刚生成的这一批次
            for num_atoms, data in mols_dict.items():
                # 处理 metadata（如 rec_src, center 等非分子坐标信息）
                if not isinstance(num_atoms, int):
                    if num_atoms not in filtered_mols_dict:
                        filtered_mols_dict[num_atoms] = data
                    continue

                batch_size = len(data['_atomic_numbers'])
                for i in range(batch_size):
                    if valid_count >= target_valid_mols:
                        break  # 如果已经凑齐 10 个，立刻停止提取

                    atomic_numbers = data['_atomic_numbers'][i]
                    positions = data['_positions'][i]

                    # 核心过滤器：只接受全都是白名单有机元素的分子
                    if set(atomic_numbers).issubset(ALLOWED_ATOMS):
                        if num_atoms not in filtered_mols_dict:
                            filtered_mols_dict[num_atoms] = {'_atomic_numbers': [], '_positions': []}

                        filtered_mols_dict[num_atoms]['_atomic_numbers'].append(atomic_numbers)
                        filtered_mols_dict[num_atoms]['_positions'].append(positions)
                        valid_count += 1

                if valid_count >= target_valid_mols:
                    break

        # 保存结果
        output_file = os.path.join(output_dir, 'generated_molecules.pkl')
        import pickle
        with open(output_file, 'wb') as f:
            pickle.dump(filtered_mols_dict, f)

        if valid_count == target_valid_mols:
            logger.info(f"Success! Exactly {valid_count} organic molecules generated and saved to {output_file}")
        else:
            logger.warning(f"Stopped after {max_attempts} attempts. Generated {valid_count} organic molecules.")

    except Exception as e:
        logger.error(f"GraphBP Generation failed: {e}")
        traceback.print_exc()