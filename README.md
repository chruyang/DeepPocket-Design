# 💊 Pocketspot: AI-Driven Drug Discovery Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Framework-Django_3.2-green?logo=django&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-1.12.1-orange?logo=pytorch&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-11.3-purple?logo=nvidia&logoColor=white)
![OpenMM](https://img.shields.io/badge/Simulation-OpenMM-red?logo=opensourceinitiative&logoColor=white)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)

**Integrated AI Platform for Cryptic Pocket-Based Drug Discovery**

</div>

**DeepPocket Design (Pocketspot)** is an integrated AI drug discovery platform that focuses on solving the challenging problem of "cryptic pockets" in drug development. This platform combines deep learning prediction, physics simulation, and generative AI to achieve a fully automated pipeline from protein structure to lead compound generation.

---

## 🚀 Core Pipeline

1.  **🎯 Target Identification**
    * **Core Algorithm**: [PocketMiner](https://github.com/PIG-group/PocketMiner) (GVP-GNN)
    * **Function**: Analyze static protein structures (`.pdb`) to predict potential cryptic binding sites.
    
2.  **🌪️ Conformation Induction**
    * **Core Engine**: [OpenMM](https://openmm.org/) (Molecular Dynamics)
    * **Function**: Perform rapid molecular dynamics simulation (MD) on proteins, inducing cryptic pockets to "open" through physical relaxation to capture optimal binding conformations. Includes automated missing atom repair using PDBFixer.

3.  **🧪 De Novo Molecule Generation**
    * **Core Algorithm**: [GraphBP](https://github.com/PIG-group/GraphBP)
    * **Function**: Generate drug-like molecules with geometric complementarity to target sites based on opened pocket structures using 3D graph neural networks.

---

## 🛠️ Installation Guide

### 1. Environment Setup (Conda)

This project requires a **Linux** environment and **NVIDIA GPU** (RTX 3090 or higher recommended for accelerated MD simulation). 

We recommend using `Conda` (or `Mamba`) to build the core physics engine to ensure proper C++ compiler and CUDA hook integrations.

```bash
# 1. Create and activate virtual environment
conda create -n deeppocket python=3.8 -y
conda activate deeppocket

# 2. Install core physics engine (OpenMM) and robust PDBFixer
conda install -c conda-forge openmm cudatoolkit=11.3 pdbfixer=1.8.1 mdtraj -y

```

### 2. Install Python Dependencies

Due to the complex native dependencies of 3D Graph Neural Networks, please follow these steps to install the deep learning frameworks using pre-built wheels, preventing local C++ compilation errors:

```bash
# 1. Install PyTorch (Specify CUDA 11.3)
pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1+cu113 --extra-index-url [https://download.pytorch.org/whl/cu113](https://download.pytorch.org/whl/cu113)

# 2. Install PyG core components (Must use official wheels matching the PyTorch version)
pip install torch-scatter torch-sparse torch-cluster torch-spline-conv torch-geometric -f [https://data.pyg.org/whl/torch-1.12.1+cu113.html](https://data.pyg.org/whl/torch-1.12.1+cu113.html)

# 3. Install the rest of the requirements (Web, ML, Chemistry libraries)
pip install -r requirements.txt

```

### 3. Download Model Weights

Due to file size limitations, model weights are not included in the repository. Please download the following weights and place them in the `models/` directory:

* **PocketMiner**: Place the `best_task1_gvp_fold0` folder into `modules/gvp-pocket_pred/gvp-pocket_pred/models/`
* **GraphBP**: Place `model_33.pth` into `modules/GraphBP/GraphBP/trained_model/`

*(Note: Depending on your exact structure, ensure weights are placed exactly where `pipeline/bridge.py` expects them).*

---

## 🏃‍♂️ Usage

### 1. Start Web Server

Navigate to the `app` directory and start the Django asynchronous service:

```bash
cd app
python manage.py runserver 0.0.0.0:8000

```

### 2. Access the Platform

* **Local Access**: Open your browser and visit `http://localhost:8000`
* **Remote Access**: If running on cloud instances (e.g., AutoDL), use **Cloudflare Tunnel** for safe port forwarding:
```bash
cloudflared tunnel --url http://localhost:8000

```



### 3. Operation Workflow

1. Upload a protein PDB file through the web interface.
2. Click **"Run AI Pipeline"**.
3. The system will automatically execute in the background: site prediction → atom fixing → GPU-accelerated simulation → molecule generation.
4. Download the generated molecule files (`.pkl` or `.sdf`) upon completion.

---

## ⚠️ Important Notes

1. **Memory Usage**: Both TensorFlow (PocketMiner) and OpenMM (MD) consume GPU memory. The backend will automatically manage memory allocation, but ensure no other heavy AI tasks are running concurrently.
2. **Runtime**: Full MD simulations and generations take time. The frontend will ping the server every 3 seconds for updates. A typical demo task (5000 MD steps) takes about 2-3 minutes.
3. **PDB Constraints**: Ensure your input `.pdb` file contains standard amino acids. The backend will attempt to strip solvents and fix missing atoms automatically.

---

## 📚 References & Acknowledgements

This project integrates the following excellent open-source algorithms:

* **PocketMiner**: [Meller, A. et al. "Predicting cryptic pockets from single protein structures using the PocketMiner optical flow network." Nature Communications (2023)](https://www.nature.com/articles/s41467-023-37607-2)
* **GraphBP**: [Liu, M. et al. "Generating 3D Molecules for Target Protein Binding." ICML (2022)](https://arxiv.org/abs/2202.09916)

### Related Resources

* [OpenMM Documentation](http://docs.openmm.org/)
* [RDKit Cheminformatics](https://www.rdkit.org/)

---

## 📄 License

This project is licensed under the [MIT License](https://www.google.com/search?q=LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to improve the AI4Science pipeline.
