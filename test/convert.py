import os
import sys
import pickle
import numpy as np
from rdkit import Chem

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)

sys.path.append(os.path.join(PROJECT_ROOT, 'modules', 'GraphBP', 'GraphBP'))

try:
    from utils.bond_adding import BondAdder
except ImportError as e:
    print(f"导入失败: {e}。")
    print("请先运行: conda install -c conda-forge openbabel -y")
    sys.exit(1)


def convert_pkl_to_sdf(pkl_path, sdf_path):
    print(f"正在读取 {pkl_path} ...")
    with open(pkl_path, 'rb') as f:
        mol_dicts = pickle.load(f)

    bond_adder = BondAdder()
    writer = Chem.SDWriter(sdf_path)

    success_count = 0
    fail_count = 0

    for key, data in mol_dicts.items():
        if not isinstance(key, int):
            continue

        num_atom = key
        atomic_numbers_batch = data['_atomic_numbers']
        positions_batch = data['_positions']
        num_mols_in_batch = len(atomic_numbers_batch)

        for i in range(num_mols_in_batch):
            atomic_numbers = atomic_numbers_batch[i]
            positions = positions_batch[i]

            try:
                rd_mol, _ = bond_adder.make_mol(atomic_numbers, positions)
                if rd_mol is not None:
                    rd_mol.SetProp("_Name", f"GraphBP_Mol_{success_count + 1}_atoms_{num_atom}")
                    writer.write(rd_mol)
                    success_count += 1
            except Exception as e:
                fail_count += 1

    writer.close()
    print("-" * 30)
    print(f"🎉 转换完成！")
    print(f"✅ 成功重构并保存: {success_count} 个分子")
    print(f"❌ 几何异常被丢弃: {fail_count} 个分子")
    print(f"📁 已保存至: {sdf_path}")


if __name__ == "__main__":
    PKL_FILE = os.path.join(TEST_DIR, 'test1/generated_molecules.pkl')

    SDF_FILE = os.path.join(TEST_DIR, 'test1/generated_molecules.sdf')

    if not os.path.exists(PKL_FILE):
        print(f"找不到文件: {PKL_FILE}，请检查路径是否正确。")
    else:
        convert_pkl_to_sdf(PKL_FILE, SDF_FILE)