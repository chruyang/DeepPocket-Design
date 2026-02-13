def extract_residue_ids_from_pdb(pdb_file_path):
    """
    从 .pdb 文件中提取残基ID，并去重。

    参数：
    - pdb_file_path: .pdb 文件的路径。

    返回值：
    - residue_ids: 提取的唯一残基ID列表。
    """
    residue_ids = []  # 使用列表来存储残基ID

    # 使用集合来记录已经添加的残基ID，确保唯一性
    seen_ids = set()

    # 打开pdb文件
    with open(pdb_file_path, "r") as pdb_file:
        # 遍历文件的每一行
        for line in pdb_file:
            # 检查是否以 "ATOM" 开头
            if line.startswith("ATOM"):
                # 使用空格分割行，并取第四、第五和第六个元素作为残基ID的一部分
                columns = line.split()
                residue_id = "-".join(columns[3:6])
                # 如果残基ID没有出现过，则添加到列表中
                if residue_id not in seen_ids:
                    residue_ids.append(residue_id)
                    seen_ids.add(residue_id)  # 将残基ID添加到集合中，标记为已添加

    return residue_ids

