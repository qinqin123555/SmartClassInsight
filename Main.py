import time
import sys
import os
import traceback
import csv
import cv2
from QssLoader import QSSLoader
from precess_bar import ProgressBar
import numpy as np
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QWidget, QHeaderView, QTableWidgetItem, QAbstractItemView, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QCoreApplication
from PIL import ImageFont
from ultralytics import YOLO
from whisper_asr import WhisperIntegrator

# 添加路径
sys.path.append('UI')
from UiMain import Ui_MainWindow
import alltools as tools
import Config
import site
try:
    sys.path.append(site.getusersitepackages())
except Exception:
    pass

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)


        self.ui = Ui_MainWindow() ## 加载UI设计
        self.ui.setupUi(self)
        self.init_system() # 系统初始化

    def init_system(self):
        """系统初始化"""
        # 尺寸设置
        self.show_size = (800, 400)
        
        # 基本变量
        self.org_path = self.cap = None
        self.is_camera_open = False
        self.orig_results = None
        self.orig_img = None 
        
        # 初始化状态
        self.video_start_time = None
        self.results_history = []  # 累计检测结果
        self.displayed_det_count = 0  # 已显示的检测条目数量
        self.last_frame = None  # 最近一帧图像用于截图
        self.asr_results = []
        self.displayed_asr_count = 0
        self.last_asr_text = ""
        self.whisper_integrator = WhisperIntegrator(model_size="base", language="zh")
        
        # 加载模型和资源
        self.load_resources()
        
        # 缓存UI控件
        self.ui_controls = self.cache_ui_controls()
        
        # 初始化UI
        self.init_ui()
        
        # 连接信号
        self.connect_signals()
        
        # 加载样式
        self.load_stylesheet()
        
        # 初始化状态
        self.reset_detection_data()

    def reset_detection_data(self): #重置检测数据
        """重置检测数据"""
        self.location_list = []
        self.cls_list = []
        self.conf_list = []

    def load_resources(self):
        """加载模型和字体"""
        self.model = YOLO(Config.model_path, task='detect')
        self.model(np.zeros((48, 48, 3)))  # 预热模型
        self.fontC = ImageFont.load_default()
        
        # 颜色工具
        self.colors = tools.Colors()
        
        # 视频定时器
        self.timer_camera = QTimer(self)
        self.timer_camera.setInterval(1)

    def cache_ui_controls(self): #缓存UI控件
        """缓存UI控件"""
        ui_controls = {
            'value_time': None, 'value_objects': None, 'value_type': None, 'value_conf': None,
            'label_xmin': None, 'label_ymin': None, 'label_xmax': None, 'label_ymax': None
        }
        
        if not hasattr(self.ui, 'statsFrame'):
            return ui_controls
        
        # 查找时间显示控件
        labels = {
            "分析用时": 'value_time', "目标数量": 'value_objects',
            "行为类型": 'value_type', "置信度": 'value_conf'
        }
        
        position_labels = {
            "Xmin:": 'label_xmin', "Ymin:": 'label_ymin',
            "Xmax:": 'label_xmax', "Ymax:": 'label_ymax'
        }
        
        for child in self.ui.statsFrame.findChildren(QLabel):
            text = child.text()
            if text in labels:
                ui_controls[labels[text]] = self.find_label_after(child)
            elif text in position_labels:
                ui_controls[position_labels[text]] = child
                child.setMinimumWidth(70)
                
        return ui_controls

    def find_label_after(self, ref_label): #查找与给定标签位置相同的后续标签
        """查找与给定标签位置相同的后续标签"""
        y_pos = ref_label.geometry().top()
        for label in self.ui.statsFrame.findChildren(QLabel):
            if label != ref_label and abs(label.geometry().top() - y_pos) < 5:
                return label
        return None

    def init_ui(self): #初始化UI组件
        """初始化UI组件"""
        # 表格设置
        if hasattr(self.ui, 'tableWidget'):
            self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
            self.ui.tableWidget.setColumnWidth(0, 80)
            self.ui.tableWidget.setColumnWidth(1, 350)
            self.ui.tableWidget.setColumnWidth(2, 120)
            self.ui.tableWidget.setColumnWidth(3, 100)
            self.ui.tableWidget.setColumnWidth(4, 300)
            self.ui.tableWidget.setMinimumHeight(300)
        
        # 设置关注行为下拉框
        if hasattr(self.ui, 'behaviorComboBox'):
            self.ui.behaviorComboBox.clear()
            self.ui.behaviorComboBox.addItems(["所有行为"] + Config.CH_names)
            
        # 按钮尺寸调整
        for btn_name in ['PicBtn', 'VideoBtn', 'CapBtn', 'ExitBtn']:
            if hasattr(self.ui, btn_name):
                getattr(self.ui, btn_name).setMinimumHeight(40)

    def connect_signals(self): #将UI组件与业务方法关联：
        """连接信号与槽 将UI组件与业务方法关联："""
        # 建立用户界面控件事件（信号）与系统功能（槽函数）之间的连接关系
        self.ui.PicBtn.clicked.connect(self.open_img)
        self.ui.comboBox.activated.connect(self.update_target_selection)
        self.ui.CapBtn.clicked.connect(self.toggle_camera)
        self.ui.ExitBtn.clicked.connect(QCoreApplication.quit)
        self.ui.VideoBtn.clicked.connect(self.open_video)
        self.ui.ExportBtn.clicked.connect(self.export_results)
        
        # 行为选择
        if hasattr(self.ui, 'behaviorComboBox'):
            self.ui.behaviorComboBox.currentTextChanged.connect(self.filter_behavior)
        
        self.whisper_integrator.connect_signals(
            result_callback=self.on_asr_result,
            status_callback=self.on_asr_status
        )

    def on_asr_result(self, result):
        self.asr_results.append(result)
        self.last_asr_text = result.text
        self.update_asr_display()
    
    def on_asr_status(self, status):
        print(f"ASR状态: {status}")

    def load_stylesheet(self):
        """加载样式表"""
        style_file = 'style.css'
        qss = QSSLoader.read_qss_file(style_file)
        self.setStyleSheet(qss)

    def filter_behavior(self, behavior): #过滤显示的行为
        """过滤显示的行为"""
        if not behavior or self.orig_results is None or self.orig_img is None:
            return
            
        # 修复: 检查图像是否有效
        if self.orig_img.size == 0:
            return
            
        if behavior == "所有行为":
            self.update_display(self.orig_results.plot())
            return
            
        try:
            idx = Config.CH_names.index(behavior)
            boxes = self.orig_results.boxes
            if not boxes:
                return
                
            # 过滤出指定类的目标
            xyxy = boxes.xyxy.tolist()
            cls_list = boxes.cls.tolist()
            conf_list = boxes.conf.tolist()
            
            filtered = [(x, c, conf) for x, c, conf in zip(xyxy, cls_list, conf_list) 
                       if int(c) == idx and len(x) == 4]
            
            # 如果没有找到匹配项
            if not filtered:
                self.update_display(self.orig_img.copy())
                return
                
            # 在原图上绘制过滤后的目标
            display_img = self.orig_img.copy()
            for x, c, conf in filtered:
                color = self.colors(int(c), True)
                tools.drawRectBox(display_img, list(map(int, x)), 
                                Config.CH_names[int(c)], self.fontC, color)
            
            # 更新UI
            self.location_list = [list(map(int, x)) for x, _, _ in filtered]
            self.cls_list = [int(c) for _, c, _ in filtered]
            self.conf_list = [f'{conf*100:.2f} %' for _, _, conf in filtered]
            
            self.update_display(display_img)
            self.update_ui_data()
            
        except Exception as e:
            print(f"行为过滤错误: {e}")

    def open_img(self):
        """打开并处理单张图片"""
        self.close_camera() # 确保摄像头关闭
        # 清空历史与表格
        self.results_history = []
        self.displayed_det_count = 0
        if hasattr(self.ui, 'tableWidget'):
            self.ui.tableWidget.setRowCount(0)
        
        file_path, _ = QFileDialog.getOpenFileName(self, '打开图片', './', 
                                                  "Image files (*.jpg *.jpeg *.png)")
        if file_path:
            self.process_image(file_path)

    def process_image(self, img_path):
        """处理单张图片检测"""
        try:
            # 读取图像
            img = tools.img_cvread(img_path)
            if img is None or img.size == 0:  # 检查图像是否有效
                QMessageBox.warning(self, "错误", "无法读取图像文件")
                return
                
            self.org_path = img_path
            self.orig_img = img.copy() # 保存一个副本用于后续的过滤操作
            
            # 目标检测
            start_time = time.time()
            results = self.model(img_path)[0]
            elapsed = time.time() - start_time
            # 处理时间
            self.update_label('value_time', f'{elapsed:.3f} s')
            
            # 提取结果
            boxes = results.boxes
            # boxes.xyxy: 边界框坐标（左上x,左上y, 右下x,右下y）
            # boxes.cls: 检测到的类别ID
            # boxes.conf: 置信度（0-1）
            if boxes.xyxy is not None:
                self.location_list = [list(map(int, x)) for x in boxes.xyxy.tolist()]
                self.cls_list = [int(c) for c in boxes.cls.tolist()]
                self.conf_list = [f'{conf*100:.2f} %' for conf in boxes.conf.tolist()]
            else:
                self.reset_detection_data()

            # 将检测结果转换为整数位置坐标
            # 存储类别ID列表
            # 将置信度转换为百分比格式字符串
            # 如果没有检测到目标，则重置相关数据
                
            # 存储原始结果
            self.orig_results = results
            # 建立累计记录
            self.results_history = []
            self.displayed_det_count = 0
            for loc, cls, conf in zip(self.location_list, self.cls_list, self.conf_list):
                self.results_history.append({
                    'path': self.org_path,
                    'type': Config.CH_names[cls],
                    'conf': self.conf_list[self.cls_list.index(cls)] if isinstance(conf, str) else f"{float(conf)*100:.2f} %",
                    'loc': loc
                })
            
            # 显示结果
            if hasattr(self.ui, 'behaviorComboBox'):
                current_behavior = self.ui.behaviorComboBox.currentText()
                if current_behavior != "所有行为":
                    self.filter_behavior(current_behavior)
                else:
                    self.update_display(results.plot())
                    self.update_ui_data()
                    self.update_table()
            else:
                self.update_display(results.plot())
                self.update_ui_data()
                self.update_table()
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"图片处理失败: {str(e)}")
            traceback.print_exc()
    # 检测结果可视化 -目标位置、类别、置信度
    def update_ui_data(self):
        """更新UI显示"""
        # 更新路径显示
        if hasattr(self.ui, 'PiclineEdit'):
            self.ui.PiclineEdit.setText(self.org_path)
            
        # 目标数量
        count = len(self.cls_list)
        self.update_label('value_objects', str(count))
        
        # 目标选择下拉框
        if hasattr(self.ui, 'comboBox'):
            self.ui.comboBox.clear()
            self.ui.comboBox.addItem('全部')
            for i, c in enumerate(self.cls_list):
                self.ui.comboBox.addItem(f"{Config.CH_names[c]}_{i}")
                
            self.ui.comboBox.setDisabled(False)
        
        # 目标信息
        if count > 0:
            self.update_label('value_type', Config.CH_names[self.cls_list[0]])
            self.update_label('value_conf', self.conf_list[0])
            self.update_label('label_xmin', str(self.location_list[0][0]))
            self.update_label('label_ymin', str(self.location_list[0][1]))
            self.update_label('label_xmax', str(self.location_list[0][2]))
            self.update_label('label_ymax', str(self.location_list[0][3]))
        else:
            self.reset_target_info()
        
        # 更新表格
        self.update_table()

    def reset_target_info(self):
        """重置目标信息"""
        self.update_label('value_type', '')
        self.update_label('value_conf', '')
        self.update_label('label_xmin', '')
        self.update_label('label_ymin', '')
        self.update_label('label_xmax', '')
        self.update_label('label_ymax', '')

    def update_label(self, label_name, text):
        """更新标签文本"""
        if label_name in self.ui_controls and self.ui_controls[label_name]:
            self.ui_controls[label_name].setText(text)

    def update_display(self, img):
        """​​图像显示适配​​"""
        if hasattr(self.ui, 'label_show'):
            # 计算合适的尺寸
            h, w, _ = img.shape
            ratio = w / h
            if ratio >= self.show_size[0] / self.show_size[1]:
                new_w = self.show_size[0]
                new_h = int(new_w / ratio)
            else:
                new_h = self.show_size[1]
                new_w = int(new_h * ratio)
            
            # 调整大小并显示
            resize_img = cv2.resize(img, (new_w, new_h))
            pixmap = tools.cvimg_to_qpiximg(resize_img)
            self.ui.label_show.setPixmap(pixmap)
            self.ui.label_show.setAlignment(Qt.AlignCenter)
            if hasattr(self.ui, 'subtitleOverlay'):
                lw = self.ui.label_show.width()
                lh = self.ui.label_show.height()
                bar_h = 64
                x = 10
                y = lh - bar_h - 10 if lh >= bar_h + 10 else 0
                self.ui.subtitleOverlay.setGeometry(x, y, max(10, lw - 20), bar_h)

    def update_table(self):
        """增量更新结果表格（累计显示）"""
        if not hasattr(self.ui, 'tableWidget'):
            return
        new_results = self.results_history[self.displayed_det_count:]
        for idx, rec in enumerate(new_results, start=self.displayed_det_count + 1):
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            items = [
                QTableWidgetItem(str(idx)),
                QTableWidgetItem(rec.get('path') or (self.org_path or "实时监控")),
                QTableWidgetItem(rec.get('type') or ""),
                QTableWidgetItem(rec.get('conf') or ""),
                QTableWidgetItem(str(rec.get('loc') or []))
            ]
            for col, item in enumerate(items):
                if col in [0, 2, 3]:
                    item.setTextAlignment(Qt.AlignCenter)
                self.ui.tableWidget.setItem(row, col, item)
        self.displayed_det_count = len(self.results_history)
        if self.ui.tableWidget.rowCount() > 0:
            self.ui.tableWidget.scrollToBottom()
    

    def close_camera(self):
        """关闭摄像头"""
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.timer_camera.isActive():
            self.timer_camera.stop()
            
        if hasattr(self.ui, 'CaplineEdit'):
            self.ui.CaplineEdit.setText('摄像头未开启')
            
        self.is_camera_open = False
        self.reset_detection_data()
        
        self.video_start_time = None

    def toggle_camera(self):
        """切换摄像头状态"""
        if self.is_camera_open:
            self.close_camera()
        else:
            self.open_camera()

    def open_camera(self):
        """打开摄像头"""
        self.close_camera()
        
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                QMessageBox.warning(self, "错误", "无法打开摄像头")
                return
                
            self.is_camera_open = True
            if hasattr(self.ui, 'CaplineEdit'):
                self.ui.CaplineEdit.setText('摄像头开启')
                
            # 清空表格和下拉框
            if hasattr(self.ui, 'tableWidget'):
                self.ui.tableWidget.setRowCount(0)
                
            if hasattr(self.ui, 'comboBox'):
                self.ui.comboBox.clear()
                self.ui.comboBox.setDisabled(True)
            
            # 记录开始时间
            
            # 记录开始时间
                
            # 连接定时器
            self.timer_camera.timeout.connect(self.process_frame)
            self.timer_camera.start()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"摄像头启动失败: {str(e)}")
            self.close_camera()

    def open_video(self):
        """打开视频文件"""
        if self.is_camera_open:
            self.close_camera()
            
        file_path, _ = QFileDialog.getOpenFileName(self, '打开视频', './', 
                                                  "Video files (*.avi *.mp4)")
        if file_path:
            self.org_path = file_path
            if hasattr(self.ui, 'VideolineEdit'):
                self.ui.VideolineEdit.setText(file_path)
            # 清空历史与表格
            self.results_history = []
            self.displayed_det_count = 0
            self.last_frame = None
            if hasattr(self.ui, 'tableWidget'):
                self.ui.tableWidget.setRowCount(0)
            
            # 清空之前结果
            self.asr_results = []
            self.displayed_asr_count = 0
            self.last_asr_text = ""
            self.whisper_integrator.process_video(file_path)
                
            self.cap = cv2.VideoCapture(file_path)
            if self.cap.isOpened():
                self.video_start_time = time.time()
                self.timer_camera.timeout.connect(self.process_frame)
                self.timer_camera.start()
                
                if hasattr(self.ui, 'comboBox'):
                    self.ui.comboBox.setDisabled(True)
            else:
                QMessageBox.warning(self, "错误", "无法打开视频文件")

    def process_frame(self):
        """处理视频帧 实时处理视频流中的每一帧图像并进行行为检测"""
        """确认视频捕获对象存在且已打开读取当前帧，如果读取失败则关闭视频源并返回"""
        if not self.cap or not self.cap.isOpened():
            return
            
        ret, frame = self.cap.read()
        if not ret:
            self.close_camera()
            return
            
        try:
            # 计算当前时间戳
            current_time = time.time() - self.video_start_time if self.video_start_time else 0
            
            # 目标检测
            start_time = time.time()
            results = self.model(frame)[0]
            elapsed = time.time() - start_time
            
            self.update_label('value_time', f'{elapsed:.3f} s')
            
            # 提取结果
            boxes = results.boxes
            if boxes.xyxy is not None:
                self.location_list = [list(map(int, x)) for x in boxes.xyxy.tolist()]
                self.cls_list = [int(c) for c in boxes.cls.tolist()]
                self.conf_list = [f'{conf*100:.2f} %' for conf in boxes.conf.tolist()]
            else:
                self.reset_detection_data()
            # 保存最近一帧用于截图
            self.last_frame = frame.copy()
            # 累计记录当前帧检测结果
            for loc, cls, conf in zip(self.location_list, self.cls_list, self.conf_list):
                self.results_history.append({
                    'path': self.org_path if self.org_path else "实时监控",
                    'type': Config.CH_names[cls],
                    'conf': conf,
                    'loc': loc
                })
                
            # 显示结果
            if hasattr(self.ui, 'behaviorComboBox'):
                behavior = self.ui.behaviorComboBox.currentText()
                if behavior == "所有行为":
                    display_img = results.plot()
                else:
                    try:
                        idx = Config.CH_names.index(behavior)
                        display_img = frame.copy()
                        for loc, c, _ in zip(self.location_list, self.cls_list, self.conf_list):
                            if int(c) == idx:
                                color = self.colors(int(c), True)
                                tools.drawRectBox(display_img, loc, 
                                                Config.CH_names[int(c)], 
                                                self.fontC, color)
                    except:
                        display_img = results.plot()
            else:
                display_img = results.plot()
                
            if hasattr(self.ui, 'subtitleOverlay'):
                self.ui.subtitleOverlay.setText(self.last_asr_text or "")
            self.update_display(display_img)
            
            # 目标数量
            count = len(self.cls_list)
            self.update_label('value_objects', str(count))
            
            # 目标信息
            if count > 0:
                self.update_label('value_type', Config.CH_names[self.cls_list[0]])
                self.update_label('value_conf', self.conf_list[0])
                self.update_label('label_xmin', str(self.location_list[0][0]))
                self.update_label('label_ymin', str(self.location_list[0][1]))
                self.update_label('label_xmax', str(self.location_list[0][2]))
                self.update_label('label_ymax', str(self.location_list[0][3]))
            else:
                self.reset_target_info()
                
            # 更新表格
            self.update_table()
            
            self.update_asr_display()
            
        except Exception as e:
            print(f"处理帧错误: {e}")
    def export_results(self):
        """导出表格数据到CSV文件，包括目标截图"""
        # 确保有数据可以导出
        if self.ui.tableWidget.rowCount() == 0:
            QMessageBox.warning(self, "导出失败", "当前没有可导出的检测结果")
            return
            
        try:
            # 获取桌面路径
            timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
            folder_name = f"安全检测结果_{timestamp}"
            candidates = [
                os.path.join(os.path.expanduser("~"), "Desktop"),
                os.path.join(os.path.expanduser("~"), "Documents"),
                os.path.join(os.getcwd(), "exports")
            ]
            folder_path = None
            for base in candidates:
                try:
                    target = os.path.join(base, folder_name)
                    os.makedirs(target, exist_ok=True)
                    folder_path = target
                    break
                except Exception:
                    continue
            if folder_path is None:
                raise PermissionError("无法创建导出目录")
            # 生成文件名(带时间戳)
            timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_hhmmss")
            folder_name = f"安全检测结果_{timestamp}"
            
            # 创建文件夹
            os.makedirs(folder_path, exist_ok=True)
            
            # 准备导出数据
            data = []
            # 表头（仅检测结果）
            headers = ["序号", "文件名", "检测时间", "行为类型", "置信度", "位置坐标", "状态", "截图文件名"]
            data.append(headers)
            
            # 当前时间
            current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            
            # 源文件名称
            source_name = "实时监控"  # 默认为实时监控
            if self.org_path:
                source_name = os.path.basename(self.org_path)
            
            # 获取原始图像（如果是图片模式）
            base_image = None
            if self.orig_img is not None:
                base_image = self.orig_img
            elif hasattr(self, 'last_frame') and self.last_frame is not None:
                base_image = self.last_frame
            
            # 提取表格数据并保存截图
            for row in range(self.ui.tableWidget.rowCount()):
                # 普通检测结果
                coord_item = self.ui.tableWidget.item(row, 4)  # 位置坐标在第4列
                location_str = coord_item.text()
                location_list = self.parse_location(location_str)
                
                if location_list and len(location_list) == 4 and base_image is not None:
                    xmin, ymin, xmax, ymax = location_list
                    height, width = base_image.shape[:2]
                    xmin = max(0, min(int(xmin), width - 1))
                    ymin = max(0, min(int(ymin), height - 1))
                    xmax = max(0, min(int(xmax), width - 1))
                    ymax = max(0, min(int(ymax), height - 1))
                    if xmin < xmax and ymin < ymax:
                        cropped_img = base_image[ymin:ymax, xmin:xmax]
                        if cropped_img.size > 0:
                            img_name = f"目标_{row+1}.jpg"
                            img_path = os.path.join(folder_path, img_name)
                            ok, buf = cv2.imencode('.jpg', cropped_img)
                            if ok:
                                buf.tofile(img_path)
                            else:
                                cv2.imwrite(img_path, cropped_img)
                        else:
                            img_name = "无有效截图"
                    else:
                        img_name = "坐标无效"
                else:
                    img_name = "无原始图像"
                
                row_data = [
                    self.ui.tableWidget.item(row, 0).text(),
                    source_name,
                    current_time,
                    self.ui.tableWidget.item(row, 2).text(),
                    self.ui.tableWidget.item(row, 3).text(),
                    location_str,
                    "正常",
                    img_name
                ]
                
                data.append(row_data)
            
            # 写入CSV文件
            csv_name = f"检测结果_{timestamp}.csv"
            csv_path = os.path.join(folder_path, csv_name)
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            
            if self.asr_results:
                asr_csv_name = f"ASR识别结果_{timestamp}.csv"
                asr_csv_path = os.path.join(folder_path, asr_csv_name)
                self.whisper_integrator.export_results(asr_csv_path)
            
            # 创建HTML报告（可选）
            self.create_html_report(folder_path, data)
                
            # 提示用户导出成功
            export_msg = f"结果已导出到: {folder_path}\n包含CSV文件和所有目标截图"
            if self.asr_results:
                export_msg += f"\nASR识别结果已单独导出"
            QMessageBox.information(self, "导出成功", export_msg)
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出过程中出错: {str(e)}")
            traceback.print_exc()
    
    def parse_location(self, location_str):
        """从字符串中解析位置坐标"""
        try:
            # 去除方括号和空格
            cleaned = location_str.strip('[]').replace(' ', '')
            # 分割为数字列表
            return [int(x) for x in cleaned.split(',')]
        except:
            return None
    
    def draw_asr_overlay(self, img, text):
        h, w = img.shape[:2]
        bar_h = 64
        y1 = max(0, h - bar_h)
        overlay = img.copy()
        cv2.rectangle(overlay, (0, y1), (w, h), (0, 0, 0), -1)
        img = cv2.addWeighted(overlay, 0.5, img, 0.5, 0)
        max_len = 40
        lines = [text[i:i + max_len] for i in range(0, len(text), max_len)]
        y = y1 + 8
        for line in lines[:2]:
            img = tools.cv2AddChineseText(img, line, (10, y), (255, 255, 255), 26)
            y += 28
        return img
    
    def update_asr_display(self):
        if not hasattr(self.ui, 'tableWidget'):
            return
        new_results = self.asr_results[self.displayed_asr_count:]
        for result in new_results:
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            items = [
                QTableWidgetItem("ASR"),
                QTableWidgetItem(self.org_path if self.org_path else "实时监控"),
                QTableWidgetItem("语音识别"),
                QTableWidgetItem(f"{result.start_time:.2f}s-{result.end_time:.2f}s"),
                QTableWidgetItem(result.text)
            ]
            for col, item in enumerate(items):
                if col in [0, 2, 3]:
                    item.setTextAlignment(Qt.AlignCenter)
                self.ui.tableWidget.setItem(row, col, item)
            self.displayed_asr_count += 1
        if self.ui.tableWidget.rowCount() > 0:
            self.ui.tableWidget.scrollToBottom()
        if hasattr(self.ui, 'asrTableWidget'):
            start_idx = self.ui.asrTableWidget.rowCount()
            for i, result in enumerate(new_results, start=start_idx + 1):
                r = self.ui.asrTableWidget.rowCount()
                self.ui.asrTableWidget.insertRow(r)
                a_items = [
                    QTableWidgetItem(str(i)),
                    QTableWidgetItem(f"{result.start_time:.2f}s-{result.end_time:.2f}s"),
                    QTableWidgetItem(result.text)
                ]
                for c, it in enumerate(a_items):
                    if c in [0, 1]:
                        it.setTextAlignment(Qt.AlignCenter)
                    self.ui.asrTableWidget.setItem(r, c, it)
            if self.ui.asrTableWidget.rowCount() > 0:
                self.ui.asrTableWidget.scrollToBottom()
    
    def create_html_report(self, folder_path, data):
        """创建美观的HTML报告"""
        html_path = os.path.join(folder_path, "检测报告.html")
        
        create_time = QDateTime.currentDateTime().toString("yyyy年MM月dd日 HH:mm")
        target_count = len(data) - 1
        type_count = len(set(row[3] for row in data[1:]))
        report_date = QDateTime.currentDateTime().toString("yyyy年MM月dd日")
        
        # 固定CSS样式（避免格式冲突）
        css_style = """
        <style>
            .report-container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                overflow: hidden;
            }
            
            .report-header {
                background: linear-gradient(135deg, #4a7bff, #5d8eff);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .report-title {
                font-size: 28px;
                margin-bottom: 10px;
                font-weight: 600;
            }
            
            .report-subtitle {
                font-size: 16px;
                opacity: 0.9;
            }
            
            .summary-section {
                display: flex;
                justify-content: space-around;
                padding: 25px 20px;
                background: #f5f9ff;
                border-bottom: 1px solid #e0ecfd;
            }
            
            .summary-item {
                text-align: center;
            }
            
            .summary-number {
                font-size: 24px;
                font-weight: 700;
                color: #4a7bff;
                margin-bottom: 5px;
            }
            
            .summary-label {
                font-size: 14px;
                color: #718096;
            }
            
            .table-container {
                overflow-x: auto;
                padding: 25px;
            }
            
            .detection-table {
                width: 100%;
                border-collapse: collapse;
                min-width: 800px;
            }
            
            .detection-table th {
                background-color: #f0f4ff;
                padding: 15px;
                text-align: left;
                font-weight: 600;
                font-size: 15px;
                color: #2d3748;
                border-bottom: 2px solid #e0ecfd;
            }
            
            .detection-table td {
                padding: 15px;
                border-bottom: 1px solid #e0ecfd;
                vertical-align: top;
            }
            
            .detection-table tr:nth-child(even) {
                background-color: #fafcff;
            }
            
            .detection-table tr:hover {
                background-color: #f5f9ff;
            }
            
            .screenshot-cell {
                text-align: center;
            }
            
            .screenshot-img {
                max-width: 120px;
                max-height: 120px;
                border-radius: 6px;
                border: 1px solid #e0ecfd;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
                transition: transform 0.2s ease;
            }
            
            .screenshot-img:hover {
                transform: scale(1.05);
            }
            
            .behavior-type {
                font-weight: 600;
                padding: 4px 10px;
                border-radius: 4px;
                display: inline-block;
            }
            
            .report-footer {
                padding: 20px;
                text-align: center;
                border-top: 1px solid #e0ecfd;
                background-color: #f8fafc;
                color: #718096;
                font-size: 14px;
            }
            
            .confidence-label {
                font-weight: 600;
                color: #10b981;
            }
            
            .status-label {
                font-weight: 600;
                color: #10b981;
            }
        </style>
        """
        
        with open(html_path, 'w', encoding='utf-8') as f:
            # HTML头部
            f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>安全检测报告</title>
    {css_style}
</head>
<body>
    <div class="report-container">
        <div class="report-header">
            <h1 class="report-title">课堂实时检测分析报告</h1>
            <div class="report-subtitle">创建时间: {create_time}</div>
        </div>
        
        <div class="summary-section">
            <div class="summary-item">
                <div class="summary-number">{target_count}</div>
                <div class="summary-label">检测目标数</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{type_count}</div>
                <div class="summary-label">行为类型数</div>
            </div>
            <div class="summary-item">
                <div class="summary-number">{report_date}</div>
                <div class="summary-label">检测日期</div>
            </div>
        </div>
        
        <div class="table-container">
            <table class="detection-table">
                <thead>
                    <tr>
            """)
            
            # 写表头
            for header in data[0]:
                f.write(f"<th>{header}</th>")
            f.write("</tr></thead><tbody>")
            
            # 行为类型的颜色映射
            behavior_colors = {
                "使用手机": "#ffedd5",  # 橙色
                "阅读": "#dbeafe",  # 蓝色
                "举手": "#dcfce7",  # 绿色
                "写作": "#f3e8fd",  # 紫色
                "低头": "#fef3c7",  # 黄色
                "靠在桌上子": "#fef2f2",  # 红色
            }
            
            # 写数据行
            for row_idx, row in enumerate(data[1:]):
                f.write("<tr>")
                for col_idx, cell in enumerate(row):
                    if col_idx == len(row) - 1:  # 最后一列是截图文件名
                        img_path = os.path.join(folder_path, cell)
                        if os.path.exists(img_path) and cell not in ["无有效截图", "坐标无效"]:
                            f.write(f'<td class="screenshot-cell"><img src="{cell}" class="screenshot-img" alt="{cell}"></td>')
                        else:
                            f.write(f"<td>{cell}</td>")
                    elif col_idx == 3:  # 行为类型列
                        bg_color = behavior_colors.get(cell, "#f0f9ff")  # 默认为浅蓝色
                        f.write(f'<td><span class="behavior-type" style="background-color: {bg_color}">{cell}</span></td>')
                    elif col_idx == 4:  # 置信度列
                        f.write(f'<td><span class="confidence-label">{cell}</span></td>')
                    elif col_idx == 6:  # 状态列
                        f.write(f'<td><span class="status-label">{cell}</span></td>')
                    else:
                        f.write(f"<td>{cell}</td>")
                f.write("</tr>")
            
            f.write("""
                </tbody>
            </table>
        </div>
        
        <div class="report-footer">
            <p>课堂检测系统 | 版本: 最终版</p>
            <p>小组成员:王怀梽 张煜 金名扬 刘锦丰 罗颢天</p>
        </div>
    </div>
</body>
</html>
            """)

    def update_target_selection(self):
        """更新选择的目标"""
        if not hasattr(self.ui, 'comboBox') or not self.orig_results:
            return
            
        selection = self.ui.comboBox.currentText()
        if selection == '全部':
            if self.location_list:
                loc = self.location_list[0]
                cls = self.cls_list[0]
                
                self.update_label('value_type', Config.CH_names[cls])
                self.update_label('value_conf', self.conf_list[0])
                self.update_label('label_xmin', str(loc[0]))
                self.update_label('label_ymin', str(loc[1]))
                self.update_label('label_xmax', str(loc[2]))
                self.update_label('label_ymax', str(loc[3]))
                
            self.update_display(self.orig_results.plot())
        else:
            try:
                idx = int(selection.split('_')[-1])
                if idx < len(self.location_list):
                    loc = self.location_list[idx]
                    cls = self.cls_list[idx]
                    
                    # 绘制单一目标
                    img = self.orig_img.copy()
                    color = self.colors(int(cls), True)
                    tools.drawRectBox(img, loc, Config.CH_names[cls], self.fontC, color)
                    
                    # 更新UI
                    self.update_display(img)
                    self.update_label('value_type', Config.CH_names[cls])
                    self.update_label('value_conf', self.conf_list[idx])
                    self.update_label('label_xmin', str(loc[0]))
                    self.update_label('label_ymin', str(loc[1]))
                    self.update_label('label_xmax', str(loc[2]))
                    self.update_label('label_ymax', str(loc[3]))
            except Exception:
                pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
