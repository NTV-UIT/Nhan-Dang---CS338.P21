# !/bin/bash
# SBATCH -o log_train.out
# SBATCH --error=error_train.log
# SBATCH --gres=gpu:1
# SBATCH -N 1
# SBATCH --ntasks=1
# SBATCH --ntasks-per-node=1
# module load python39

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --break-system-packages
pip install -r requirements.txt --break-system-packages
# python3.9 mapper/scripts/train.py --exp_dir experiments/exp1 --batch_size 32  --description="mohawk hairstyle" 