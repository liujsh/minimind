#!/usr/bin/env bash
# Run SFT or LoRA inside the Docker container. Usage:
#  ./run_sft.sh mode [gpu_ids]
# mode: full_sft | lora
# gpu_ids: CUDA_VISIBLE_DEVICES (default 0)

MODE=${1:-lora}
GPU=${2:-0}

export CUDA_VISIBLE_DEVICES=${GPU}

if [ "${MODE}" = "full_sft" ]; then
  echo "Running full SFT (may need more GPU memory)"
  python trainer/train_full_sft.py --data_path dataset/sft_mini_512.jsonl --from_weight pretrain --save_weight full_sft_autodl --epochs 2 --batch_size 8 --learning_rate 1e-6 --use_wandb
else
  echo "Running LoRA SFT (memory-efficient)"
  python trainer/train_lora.py --data_path dataset/sft_mini_512.jsonl --from_weight pretrain --lora_name sft_mini_autodl --epochs 10 --batch_size 32 --learning_rate 1e-4 --use_wandb
fi
