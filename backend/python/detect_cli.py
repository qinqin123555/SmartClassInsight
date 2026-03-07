import argparse
import json
import sys
import os

# 使用项目原有逻辑与配置
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT)
import Config  # noqa: E402
from ultralytics import YOLO  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", "-i", required=True, help="path to image")
    args = parser.parse_args()

    img_path = args.image
    if not os.path.exists(img_path):
        print(json.dumps({"error": "image_not_found"}))
        return 1

    # 加载与 Main.py 一致的模型与类别
    model_path = Config.model_path
    if not os.path.isabs(model_path):
        model_path = os.path.join(ROOT, model_path)
    model = YOLO(model_path, task="detect")
    # 让 Ultralytics 自动选择可用的 GPU 提供者（onnxruntime-gpu 已安装时）
    results = model.predict(img_path, verbose=False)[0]

    label = None
    count = 0
    if results and results.boxes and results.boxes.cls is not None:
        # 统计每个类别出现次数，或取最高置信度
        cls_list = results.boxes.cls.tolist()
        conf_list = results.boxes.conf.tolist()
        if cls_list:
            # 选择最高置信度的类别
            max_idx = max(range(len(conf_list)), key=lambda k: conf_list[k])
            cls_id = int(cls_list[max_idx])
            label = Config.CH_names[cls_id] if 0 <= cls_id < len(Config.CH_names) else str(cls_id)
            count = sum(1 for c in cls_list if int(c) == cls_id)

    if label is None:
        print(json.dumps({"label": "无目标", "count": 0}))
        return 0

    print(json.dumps({"label": label, "count": int(count)} , ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
