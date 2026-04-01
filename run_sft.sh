#!/usr/bin/env bash
# Run SFT or LoRA inside the Docker container. Usage:
#  ./run_sft.sh mode [gpu_ids]
# mode: full_sft | lora
# gpu_ids: CUDA_VISIBLE_DEVICES (default 0)

MODE="lora"
GPU="0"
SAVE_DIR="/workspace/minimind/out"

# 简单参数解析，支持位置参数或 --save_dir=/path 或 --save_dir <path>
while [[ $# -gt 0 ]]; do
  case "$1" in
    lora|full_sft)
      MODE="$1"; shift ;;
    --save_dir)
      SAVE_DIR="$2"; shift 2 ;;
    --save_dir=*)
      SAVE_DIR="${1#*=}"; shift ;;
    --gpu=*)
      GPU="${1#*=}"; shift ;;
    [0-9]*)
      GPU="$1"; shift ;;
    *)
      echo "Unknown arg: $1"; shift ;;
  esac
done

export CUDA_VISIBLE_DEVICES=${GPU}

echo "MODE=${MODE}, GPU=${GPU}, SAVE_DIR=${SAVE_DIR}"

if [ "${MODE}" = "full_sft" ]; then
  echo "Running full SFT (may need more GPU memory)"
  python trainer/train_full_sft.py --data_path dataset/sft_mini_512.jsonl --from_weight pretrain --save_weight full_sft_autodl --epochs 2 --batch_size 8 --learning_rate 1e-6 --save_dir ${SAVE_DIR} --use_wandb
else
  echo "Running LoRA SFT (memory-efficient)"
  python trainer/train_lora.py --data_path dataset/sft_mini_512.jsonl --from_weight pretrain --lora_name sft_mini_autodl --epochs 10 --batch_size 32 --learning_rate 1e-4 --save_dir ${SAVE_DIR} --use_wandb
fi
