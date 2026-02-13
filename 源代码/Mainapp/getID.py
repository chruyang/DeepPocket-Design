pdb_file_path = "static/test.pdb"  # 替PDB文件路径
num_id = 0
ids = []
past_id = "#"
with open(pdb_file_path, 'r') as pdb_file:
    for i, line in enumerate(pdb_file):
        if i <= 3:
            continue
        fields = line.split()
        currrent_id = " ".join(fields[3:6])
        if past_id != currrent_id:
            ids.append(currrent_id)
            past_id = currrent_id
            num_id += 1
        if num_id >= 10:
            break

print(ids)

# output_file_path = "output.txt"
# with open(output_file_path, 'w') as output_file:
#     for id in ids:
#         output_file.write(id + '\n')