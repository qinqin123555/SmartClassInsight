import os
import sys
import traceback
import io
import base64
import json
import threading
import time
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT)
import Config

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174', 'http://127.0.0.1:5174'], supports_credentials=True)

# 启动时加载模型（只加载一次）
print(f"Loading model from: {Config.model_path}")
model_path = Config.model_path if os.path.isabs(Config.model_path) else os.path.join(ROOT, Config.model_path)
if not os.path.exists(model_path):
    print(f"ERROR: Model file not found: {model_path}")
    sys.exit(1)

model = YOLO(model_path, task="detect")
print(f"✓ Model loaded successfully: {model_path}")
print(f"✓ Service starting on http://0.0.0.0:5001")

# 颜色配置（RGB格式用于PIL）
COLORS = [
    (255, 56, 56),    # 红色
    (255, 157, 151),  # 粉色
    (255, 112, 31),   # 橙色
    (255, 178, 29),   # 黄色
    (207, 210, 49),   # 黄绿
    (72, 249, 10),    # 绿色
]

def get_font(size=20):
    """获取支持中文的字体"""
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
    ]
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                pass
    return ImageFont.load_default()

def draw_detection_boxes_on_frame(frame, results):
    """在视频帧上绘制检测框和标签（支持中文）"""
    if frame is None:
        return None
    
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    draw = ImageDraw.Draw(img_pil)
    font = get_font(20)
    
    detections = []
    
    if results and results.boxes and results.boxes.cls is not None:
        cls_list = results.boxes.cls.tolist()
        conf_list = results.boxes.conf.tolist()
        xyxy_list = results.boxes.xyxy.tolist()
        
        for i, (cls_id, conf, xyxy) in enumerate(zip(cls_list, conf_list, xyxy_list)):
            cls_id = int(cls_id)
            x1, y1, x2, y2 = map(int, xyxy)
            color = COLORS[cls_id % len(COLORS)]
            
            # 绘制矩形框
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            # 获取标签文本
            label = Config.CH_names[cls_id] if 0 <= cls_id < len(Config.CH_names) else str(cls_id)
            text = f"{label} {conf:.2f}"
            
            detections.append({
                "class": label,
                "confidence": round(conf, 4),
                "bbox": [round(x, 2) for x in xyxy]
            })
            
            # 计算文本大小
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 绘制标签背景
            draw.rectangle([x1, y1 - text_height - 10, x1 + text_width, y1], fill=color)
            
            # 绘制标签文字
            draw.text((x1, y1 - text_height - 5), text, fill=(255, 255, 255), font=font)
    
    img_result = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return img_result, detections

def frame_to_base64(frame):
    """将视频帧转换为Base64字符串"""
    if frame is None:
        return None
    _, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    return img_base64

def generate_video_frames(video_path, skip_frames=2):
    """生成视频帧流，边检测边返回"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {video_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0
    
    print(f"Processing video: {video_path}, FPS: {fps}, Total frames: {total_frames}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # 跳过部分帧以提高性能
        if frame_count % (skip_frames + 1) != 0:
            continue
        
        # 检测当前帧
        results = model.predict(frame, verbose=False)[0]
        
        # 绘制检测框
        annotated_frame, detections = draw_detection_boxes_on_frame(frame, results)
        
        # 获取主检测结果
        label = "无目标"
        count = 0
        if results and results.boxes and results.boxes.cls is not None:
            cls_list = results.boxes.cls.tolist()
            conf_list = results.boxes.conf.tolist()
            if cls_list:
                max_idx = max(range(len(conf_list)), key=lambda k: conf_list[k])
                cls_id = int(cls_list[max_idx])
                label = Config.CH_names[cls_id] if 0 <= cls_id < len(Config.CH_names) else str(cls_id)
                count = len(cls_list)
        
        # 计算时间戳
        timestamp = frame_count / fps if fps > 0 else 0
        
        # 转换为base64
        frame_base64 = frame_to_base64(annotated_frame)
        
        # 构建响应数据
        data = {
            "frame": frame_count,
            "timestamp": round(timestamp, 2),
            "totalFrames": total_frames,
            "label": label,
            "count": count,
            "detections": detections,
            "image": frame_base64,
            "progress": round((frame_count / total_frames) * 100, 2) if total_frames > 0 else 0
        }
        
        # 发送SSE事件，确保格式正确
        json_str = json.dumps(data)
        yield f"data: {json_str}\n"
        yield "\n"
    
    cap.release()
    print(f"Video processing completed: {frame_count} frames processed")

@app.route('/detect', methods=['POST'])
def detect():
    """单张图片检测"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "no_image"}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "empty_filename"}), 400

        temp_path = os.path.join(ROOT, "data", "temp", f"{os.getpid()}_{file.filename}")
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        file.save(temp_path)
        print(f"Processing: {file.filename}")

        try:
            results = model.predict(temp_path, verbose=False)[0]

            label = "无目标"
            count = 0
            detections = []

            if results and results.boxes and results.boxes.cls is not None:
                cls_list = results.boxes.cls.tolist()
                conf_list = results.boxes.conf.tolist()
                xyxy_list = results.boxes.xyxy.tolist()

                if cls_list:
                    max_idx = max(range(len(conf_list)), key=lambda k: conf_list[k])
                    cls_id = int(cls_list[max_idx])
                    label = Config.CH_names[cls_id] if 0 <= cls_id < len(Config.CH_names) else str(cls_id)
                    count = sum(1 for c in cls_list if int(c) == cls_id)
                    
                    for i, (c, conf, xyxy) in enumerate(zip(cls_list, conf_list, xyxy_list)):
                        detections.append({
                            "class": Config.CH_names[int(c)] if 0 <= int(c) < len(Config.CH_names) else str(int(c)),
                            "confidence": round(conf, 4),
                            "bbox": [round(x, 2) for x in xyxy]
                        })

            # 生成标注后的图片
            frame = cv2.imread(temp_path)
            annotated_img, _ = draw_detection_boxes_on_frame(frame, results)
            annotated_image_base64 = frame_to_base64(annotated_img)

            print(f"Result: {label} (count: {count})")
            
            response_data = {
                "label": label, 
                "count": count,
                "detections": detections
            }
            
            if annotated_image_base64:
                response_data["annotatedImage"] = annotated_image_base64
                response_data["annotatedImageType"] = "image/jpeg"
            
            return jsonify(response_data)

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "detection_failed", "message": str(e)}), 500

@app.route('/detect/video', methods=['POST'])
def detect_video():
    """视频流式检测 - 边播放边检测"""
    try:
        print(f"Received video detection request from: {request.remote_addr}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Request files: {list(request.files.keys())}")
        print(f"Request form: {dict(request.form)}")
        
        if 'video' not in request.files:
            print("ERROR: No video file in request")
            return jsonify({"error": "no_video"}), 400

        file = request.files['video']
        if file.filename == '':
            print("ERROR: Empty filename")
            return jsonify({"error": "empty_filename"}), 400

        # 保存视频文件
        temp_dir = os.path.join(ROOT, "data", "temp")
        os.makedirs(temp_dir, exist_ok=True)
        video_path = os.path.join(temp_dir, f"{os.getpid()}_{file.filename}")
        file.save(video_path)
        print(f"Saved video to: {video_path}")
        print(f"Processing video: {file.filename}")

        # 获取跳帧参数
        skip_frames = request.form.get('skip_frames', 2, type=int)
        print(f"Skip frames: {skip_frames}")

        def generate():
            try:
                yield from generate_video_frames(video_path, skip_frames)
            finally:
                # 清理临时文件
                if os.path.exists(video_path):
                    try:
                        os.remove(video_path)
                        print(f"Cleaned up: {video_path}")
                    except Exception as e:
                        print(f"Error cleaning up file: {e}")
                        # 延迟后再尝试删除
                        import time
                        time.sleep(1)
                        try:
                            if os.path.exists(video_path):
                                os.remove(video_path)
                                print(f"Cleaned up after delay: {video_path}")
                        except Exception as e2:
                            print(f"Failed to clean up file: {e2}")

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "video_detection_failed", "message": str(e)}), 500

@app.route('/detect/video/frame', methods=['POST'])
def detect_video_frame():
    """检测视频单帧（用于前端轮询）"""
    try:
        data = request.get_json()
        if not data or 'videoPath' not in data:
            return jsonify({"error": "no_video_path"}), 400
        
        video_path = data['videoPath']
        frame_number = data.get('frameNumber', 0)
        
        if not os.path.exists(video_path):
            return jsonify({"error": "video_not_found"}), 404
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return jsonify({"error": "cannot_open_video"}), 500
        
        # 设置帧位置
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return jsonify({"error": "frame_not_found"}), 404
        
        # 检测
        results = model.predict(frame, verbose=False)[0]
        annotated_frame, detections = draw_detection_boxes_on_frame(frame, results)
        
        # 获取主检测结果
        label = "无目标"
        count = 0
        if results and results.boxes and results.boxes.cls is not None:
            cls_list = results.boxes.cls.tolist()
            conf_list = results.boxes.conf.tolist()
            if cls_list:
                max_idx = max(range(len(conf_list)), key=lambda k: conf_list[k])
                cls_id = int(cls_list[max_idx])
                label = Config.CH_names[cls_id] if 0 <= cls_id < len(Config.CH_names) else str(cls_id)
                count = len(cls_list)
        
        # 转换为base64
        frame_base64 = frame_to_base64(annotated_frame)
        
        return jsonify({
            "frame": frame_number,
            "label": label,
            "count": count,
            "detections": detections,
            "image": frame_base64
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "frame_detection_failed", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "model": model_path})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, threaded=True)
