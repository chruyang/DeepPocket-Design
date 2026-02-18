
# 💊 DeepPocket Design: AI-Driven Drug Discovery Platform

![Python](https://img.shields.io/badge/Python-3.8-blue)
![Django](https://img.shields.io/badge/Framework-Django_3.2-green)
![CUDA](https://img.shields.io/badge/Hardware-NVIDIA_RTX_GPU-purple)
![OpenMM](https://img.shields.io/badge/Simulation-OpenMM-orange)

**DeepPocket Design** 是一个集成化的 AI 药物设计平台，专注于解决“隐性口袋（Cryptic Pockets）”的药物开发难题。该平台结合了深度学习预测、物理模拟和生成式 AI，实现从蛋白质结构到先导化合物生成的全自动流程。

---

## 🚀 核心流程 (Pipeline)

1.  **🎯 靶点识别 (Target Identification)**
    * **核心算法**: [PocketMiner](https://github.com/PIG-group/PocketMiner) (GVP-GNN)
    * **功能**: 分析静态蛋白质结构 (`.pdb`)，预测可能存在的隐性结合位点（Cryptic Pockets）。
    
2.  **🌪️ 构象诱导 (Conformation Induction)**
    * **核心引擎**: [OpenMM](https://openmm.org/) (Molecular Dynamics)
    * **功能**: 对蛋白质进行快速分子动力学模拟（MD），通过物理松弛诱导隐性口袋“张开”，捕捉最佳结合构象。

3.  **🧪 分子生成 (De Novo Generation)**
    * **核心算法**: [GraphBP](https://github.com/PIG-group/GraphBP)
    * **功能**: 基于张开的口袋结构，利用 3D 图神经网络生成与靶点几何互补的类药分子。

---

## 📂 项目结构 (Project Structure)
```text
DeepPocket-Design/
├── app/                  # [Web Layer] Django Web 服务端
│   ├── manage.py         # Django 管理入口
│   ├── pocket_server/    # 项目核心配置 (Settings, URLs)
│   └── core/             # 业务逻辑 (Views, Templates)
│
├── pipeline/             # [Logic Layer] 核心算法管线
│   ├── bridge.py         # 流程总控 (连接 PocketMiner -> MD -> GraphBP)
│   └── md_engine.py      # MD 模拟引擎 (OpenMM 封装)
│
├── modules/              # [External] 第三方算法源码
│   ├── gvp_pocket_pred/  # PocketMiner 源代码
│   └── GraphBP/          # GraphBP 源代码
│
├── models/               # [Weights] 模型权重文件 (需手动下载)
│   ├── pocketminer/      # PocketMiner 权重 (如 best_task1_gvp_fold0)
│   └── graphbp/          # GraphBP 权重 (如 model_33.pth)
│
├── static/               # 静态资源 (CSS, JS, Images)
├── templates/            # 前端 HTML 模板
└── requirements.txt      # Python 依赖清单

```

---

## 🛠️ 安装指南 (Installation)

### 1. 环境准备

本项目需要 **Linux** 环境和 **NVIDIA 显卡**（推荐 RTX 3090 或更高级别以加速 MD 模拟）。

推荐使用 `Conda` (或 `Mamba`) 进行环境管理：

```bash
# 1. 创建虚拟环境
conda create -n pocket_design python=3.8 -y
conda activate pocket_design

# 2. 安装核心物理引擎 (OpenMM) 和 CUDA 支持
# 注意：根据你的显卡驱动版本选择 cudatoolkit (这里以 11.8 为例)
conda install -c conda-forge openmm cudatoolkit=11.8 pdbfixer mdtraj -y

```

### 2. 安装 Python 依赖

```bash
pip install django==3.2.* pip install numpy pandas scipy biopython
pip install torch==1.13.1+cu117 --extra-index-url [https://download.pytorch.org/whl/cu117](https://download.pytorch.org/whl/cu117)
pip install tensorflow==2.11.0  # PocketMiner 依赖
pip install rdkit-pypi networkx

```

### 3. 下载模型权重 (Model Weights)

由于文件体积限制，模型权重未包含在代码库中。请下载以下权重并放入 `models/` 目录：

* **PocketMiner**: 将 `best_task1_gvp_fold0` 文件夹放入 `models/pocketminer/`
* **GraphBP**: 将 `model_33.pth` 放入 `models/graphbp/`

---

## 🏃‍♂️ 运行方法 (Usage)

### 1. 启动 Web 服务器

进入 `app` 目录并启动 Django 服务：

```bash
cd app
python manage.py runserver 0.0.0.0:8000

```

### 2. 访问平台

* **本地访问**: 打开浏览器访问 `http://localhost:8000`
* **远程访问**: 如果你在远程服务器 (如 AutoDL) 上运行，建议使用 **Cloudflare Tunnel** 或 **Ngrok** 进行内网穿透。

### 3. 操作流程

1. 在网页端上传蛋白质 PDB 文件。
2. 点击 **"Run Pipeline"**。
3. 系统将自动执行：预测位点 -> GPU 加速模拟 -> 生成分子。
4. 完成后下载生成的分子文件 (`.pkl` 或 `.sdf`)。

---

## ⚠️ 注意事项

1. **显存占用**: TensorFlow (PocketMiner) 和 OpenMM (MD) 都会占用显存。如果遇到 OOM 错误，请尝试在 `bridge.py` 中设置 `TF_FORCE_GPU_ALLOW_GROWTH=true`。
2. **运行时间**: MD 模拟时间取决于步数 (`steps`)。演示模式建议设为 1000-5000 步 (约 10-30秒)；生产模式建议设为 100,000+ 步。

---

## 📜 引用与致谢 (References)

本项目集成了以下优秀的开源算法：

* **PocketMiner**: [Meller, A. et al. "Predicting cryptic pockets from single protein structures using the PocketMiner optical flow network."](https://www.google.com/search?q=https://www.nature.com/articles/s41467-023-37607-2)
* **GraphBP**: [Liu, M. et al. "Generating 3D Molecules for Target Protein Binding."](https://arxiv.org/abs/2202.09916)

---

## 📄 License

[MIT License](https://www.google.com/search?q=LICENSE)
