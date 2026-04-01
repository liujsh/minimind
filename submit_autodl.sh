#!/usr/bin/env bash
set -euo pipefail

# submit_autodl.sh
# 构建镜像并运行容器的通用脚本，适用于支持 Docker 的 Autodl 平台。
# 用法示例：
#  ./submit_autodl.sh --host-dir /data/minimind --mode lora --gpus 0 --tag minimind:autodl
# 如果需要将镜像推到 Registry，设置环境变量 DOCKER_REGISTRY，例如 DOCKER_REGISTRY=registry.example.com

usage(){
  cat <<EOF
Usage: $0 --host-dir <HOST_PATH> [--mode lora|full_sft] [--gpus 0] [--tag minimind:autodl] [--save-dir /workspace/minimind/out]

Options:
  --host-dir   宿主机持久化目录（必填），会挂载到容器 /workspace/minimind
  --mode       lora 或 full_sft（默认 lora）
  --gpus       要分配的 GPU id（默认 0），传给 CUDA_VISIBLE_DEVICES
  --tag        Docker 镜像 tag（默认 minimind:autodl）
  --save-dir   容器内保存权重的目录（默认 /workspace/minimind/out）
EOF
}

HOST_DIR=""
MODE="lora"
GPU_IDS="0"
TAG="minimind:autodl"
SAVE_DIR="/workspace/minimind/out"

while [[ $# -gt 0 ]]; do
  case $1 in
    --host-dir) HOST_DIR="$2"; shift 2;;
    --mode) MODE="$2"; shift 2;;
    --gpus) GPU_IDS="$2"; shift 2;;
    --tag) TAG="$2"; shift 2;;
    --save-dir) SAVE_DIR="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

if [[ -z "$HOST_DIR" ]]; then
  echo "--host-dir is required"; usage; exit 1
fi

echo "Building Docker image: ${TAG}"
docker build -t ${TAG} .

if [[ -n "${DOCKER_REGISTRY:-}" ]]; then
  REG_TAG="${DOCKER_REGISTRY}/${TAG}"
  echo "Tagging and pushing to registry: ${REG_TAG}"
  docker tag ${TAG} ${REG_TAG}
  docker push ${REG_TAG}
  TAG=${REG_TAG}
fi

echo "Running container with image ${TAG}"

# 确保宿主目录存在
mkdir -p "${HOST_DIR}"

docker run --gpus all -it --rm \
  -v "${HOST_DIR}:/workspace/minimind" \
  -w /workspace/minimind \
  -e CUDA_VISIBLE_DEVICES="${GPU_IDS}" \
  ${TAG} \
  bash -c "./run_sft.sh ${MODE} 0 --save_dir ${SAVE_DIR} || bash"

echo "Container finished. Check ${HOST_DIR} for outputs (or ${SAVE_DIR} inside container)."
