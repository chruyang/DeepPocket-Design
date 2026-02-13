from rdkit import Chem
from rdkit.Chem import Draw

# 从PDB文件加载分子
mol = Chem.MolFromPDBFile('101m.pdb')

# 设置绘图选项
Draw.DrawingOptions.dotsPerAngstrom = 500
Draw.DrawingOptions.bondLineWidth = 2.0
for atom in mol.GetAtoms():
    atom.SetProp('atomLabel', '')
# 绘制分子
# Draw.MolToImage(mol, size=(1000, 1000))
Draw.MolToFile(mol, 'data/output.png', size=(1000, 1000))
# 显示图像


