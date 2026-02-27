import torch
from ultralytics import YOLO
model = YOLO("yolo11n.pt") 
if __name__ == '__main__':
    # 例如: 0 0.5 0.5 0.2 0.3 表示"hand-raising"
    # Use the model
    results = model.train(data='./datasets/dataset/data.yaml', epochs=15, batch=8)
    success = model.export(format='onnx')