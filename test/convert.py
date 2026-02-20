import pickle
from rdkit import Chem

pkl_file = 'test1/generated_molecules.pkl'  # 替换为您的实际路径
with open(pkl_file, 'rb') as f:
    mols = pickle.load(f)

sdf_file = 'generated_molecules.sdf'
writer = Chem.SDWriter(sdf_file)

# 遍历字典或列表保存分子
# (视 GraphBP 的输出结构而定，如果是字典列表)
for mol_data in mols:
    if isinstance(mol_data, Chem.rdchem.Mol):
        writer.write(mol_data)

writer.close()
print(f"转换成功！已保存为 {sdf_file}")