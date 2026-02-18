# 💊 DeepPocket Design: AI-Driven Drug Discovery Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Framework-Django_3.2-green?logo=django&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-1.13.1-orange?logo=pytorch&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-11.7-purple?logo=nvidia&logoColor=white)
![OpenMM](https://img.shields.io/badge/Simulation-OpenMM-red?logo=opensourceinitiative&logoColor=white)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey)

**Integrated AI Platform for Cryptic Pocket-Based Drug Discovery**

</div>

**DeepPocket Design** is an integrated AI drug discovery platform that focuses on solving the challenging problem of "cryptic pockets" in drug development. This platform combines deep learning prediction, physics simulation, and generative AI to achieve a fully automated pipeline from protein structure to lead compound generation.

---

## 🚀 Core Pipeline

1.  **🎯 Target Identification**
    * **Core Algorithm**: [PocketMiner](https://github.com/PIG-group/PocketMiner) (GVP-GNN)
    * **Function**: Analyze static protein structures (`.pdb`) to predict potential cryptic binding sites.
    
2.  **🌪️ Conformation Induction**
    * **Core Engine**: [OpenMM](https://openmm.org/) (Molecular Dynamics)
    * **Function**: Perform rapid molecular dynamics simulation (MD) on proteins, inducing cryptic pockets to "open" through physical relaxation to capture optimal binding conformations.

3.  **🧪 De Novo Molecule Generation**
    * **Core Algorithm**: [GraphBP](https://github.com/PIG-group/GraphBP)
    * **Function**: Generate drug-like molecules with geometric complementarity to target sites based on opened pocket structures using 3D graph neural networks.

---

## 📂 Project Structure

```text
DeepPocket-Design/
├── app/                  # [Web Layer] Django Web Server
│   ├── manage.py         # Django Management Entry Point
│   ├── pocket_server/    # Core Project Configuration (Settings, URLs)
│   └── core/             # Business Logic (Views, Templates)
│
├── pipeline/             # [Logic Layer] Core Algorithm Pipeline
│   ├── bridge.py         # Pipeline Controller (Connecting PocketMiner -> MD -> GraphBP)
│   └── md_engine.py      # MD Simulation Engine (OpenMM Wrapper)
│
├── modules/              # [External] Third-party Algorithm Source Code
│   ├── gvp_pocket_pred/  # PocketMiner Source Code
│   └── GraphBP/          # GraphBP Source Code
│
├── models/               # [Weights] Model Weight Files (Manual Download Required)
│   ├── pocketminer/      # PocketMiner Weights (e.g., best_task1_gvp_fold0)
│   └── graphbp/          # GraphBP Weights (e.g., model_33.pth)
│
├── static/               # Static Resources (CSS, JS, Images)
├── templates/            # Frontend HTML Templates
└── requirements.txt      # Python Dependencies List
```

---

## 🛠️ Installation Guide

### 1. Environment Setup

This project requires a **Linux** environment and **NVIDIA GPU** (RTX 3090 or higher recommended for accelerated MD simulation).

We recommend using `Conda` (or `Mamba`) for environment management:

```bash
# 1. Create virtual environment
conda create -n pocket_design python=3.8 -y
conda activate pocket_design

# 2. Install core physics engine (OpenMM) and CUDA support
# Note: Choose cudatoolkit version according to your GPU driver (11.8 used here as example)
conda install -c conda-forge openmm cudatoolkit=11.8 pdbfixer mdtraj -y
```

### 2. Install Python Dependencies

```bash
pip install django==3.2.* numpy pandas scipy biopython
pip install torch==1.13.1+cu117 --extra-index-url https://download.pytorch.org/whl/cu117
pip install tensorflow==2.11.0  # PocketMiner dependency
pip install rdkit-pypi networkx
```

### 3. Download Model Weights

Due to file size limitations, model weights are not included in the repository. Please download the following weights and place them in the `models/` directory:

* **PocketMiner**: Place the `best_task1_gvp_fold0` folder into `models/pocketminer/`
* **GraphBP**: Place `model_33.pth` into `models/graphbp/`

---

## 🏃‍♂️ Usage

### 1. Start Web Server

Navigate to the `app` directory and start the Django service:

```bash
cd app
python manage.py runserver 0.0.0.0:8000

# For production deployment, consider using:
# gunicorn pocket_server.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 2. Access the Platform

* **Local Access**: Open browser and visit `http://localhost:8000`
* **Remote Access**: If running on remote servers (like AutoDL), consider using **Cloudflare Tunnel** or **Ngrok** for tunneling.

### 3. Operation Workflow

1. Upload protein PDB file through the web interface.
2. Click **"Run Pipeline"**.
3. System will automatically execute: site prediction → GPU-accelerated simulation → molecule generation.
4. Download generated molecule files (`.pkl` or `.sdf`) upon completion.

---

## ⚠️ Important Notes

1. **Memory Usage**: Both TensorFlow (PocketMiner) and OpenMM (MD) consume GPU memory. If encountering OOM errors, try setting `TF_FORCE_GPU_ALLOW_GROWTH=true` in `bridge.py`.
2. **Runtime**: MD simulation time depends on the number of steps. Demo mode recommends 1000-5000 steps (~10-30 seconds); production mode recommends 100,000+ steps.
3. **Performance Optimization**: For better performance, ensure your NVIDIA drivers are up to date and CUDA-compatible.

---

## 📚 References & Acknowledgements

This project integrates the following excellent open-source algorithms:

* **PocketMiner**: [Meller, A. et al. "Predicting cryptic pockets from single protein structures using the PocketMiner optical flow network." Nature Communications (2023)](https://www.nature.com/articles/s41467-023-37607-2)
* **GraphBP**: [Liu, M. et al. "Generating 3D Molecules for Target Protein Binding." ICML (2022)](https://arxiv.org/abs/2202.09916)

### Related Resources
* [OpenMM Documentation](http://docs.openmm.org/)
* [RDKit Cheminformatics](https://www.rdkit.org/)
* [Protein Data Bank](https://www.rcsb.org/)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2024 DeepPocket Design Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📞 Support

* **Issues**: [GitHub Issues](https://github.com/your-username/DeepPocket-Design/issues)
* **Email**: support@deeppocket-design.org

<div align="center">

**🌟 If you find this project helpful, please give us a Star!**

</div>