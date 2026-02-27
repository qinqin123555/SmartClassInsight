# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        # 主窗口设置
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)
        MainWindow.setMinimumSize(QtCore.QSize(1920, 1080))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/ui_imgs/icons/目标检测.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet("background-color: #f5f7ff;")
        
        # 中央控件
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # 主布局 - 垂直布局
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(20, 15, 20, 15)
        self.verticalLayout.setSpacing(20)
        
        # === 顶部区域: 视频显示 ===
        self.videoFrame = QtWidgets.QFrame(self.centralwidget)
        self.videoFrame.setMinimumHeight(500)
        self.videoFrame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 16px;
                border: none;
            }
        """)
        
        self.videoLayout = QtWidgets.QVBoxLayout(self.videoFrame)
        self.videoLayout.setContentsMargins(10, 10, 10, 10)
        
        # 标题栏
        self.videoHeader = QtWidgets.QLabel(self.videoFrame)
        self.videoHeader.setText("监控画面")
        self.videoHeader.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4a7bff;
                padding: 12px 0;
                border-bottom: 2px solid #eef3ff;
            }
        """)
        self.videoLayout.addWidget(self.videoHeader)
        
        # 视频标签
        self.label_show = QtWidgets.QLabel(self.videoFrame)
        self.label_show.setObjectName("label_show")
        self.label_show.setMinimumSize(QtCore.QSize(0, 460))
        self.label_show.setAlignment(QtCore.Qt.AlignCenter)
        self.label_show.setStyleSheet("""
            QLabel {
                background-color: #f5f9ff;
                font-size: 24px;
                color: #5a7dc9;
                border-radius: 12px;
                border: 2px dashed #d1e0fe;
                margin: 10px;
                font-weight: 500;
            }
        """)
        self.label_show.setText("等待输入视频或图像...")
        self.videoLayout.addWidget(self.label_show)
        
        self.subtitleOverlay = QtWidgets.QLabel(self.label_show)
        self.subtitleOverlay.setMinimumHeight(64)
        self.subtitleOverlay.setWordWrap(True)
        self.subtitleOverlay.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.subtitleOverlay.setStyleSheet("""
            QLabel {
                background-color: rgba(0,0,0,0.4);
                color: #ffffff;
                font-size: 22px;
                border-radius: 8px;
                padding: 8px 12px;
            }
        """)
        self.subtitleOverlay.setText("")
        self.verticalLayout.addWidget(self.videoFrame)
        
        # === 中间区域: 操作栏和显示区域 ===
        self.middleLayout = QtWidgets.QHBoxLayout()
        self.middleLayout.setSpacing(20)
        
        # 检测结果表格
        self.resultsCard = QtWidgets.QFrame(self.centralwidget)
        self.resultsCard.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 16px;
                border: none;
            }
        """)
        self.resultsCard.setMinimumWidth(1000)
        self.resultsCard.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        self.resultsLayout = QtWidgets.QVBoxLayout(self.resultsCard)
        self.resultsLayout.setContentsMargins(15, 15, 15, 15)
        
        # 结果表格标题
        resultsTitle = QtWidgets.QLabel("检测结果明细")
        resultsTitle.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4a7bff;
                margin-bottom: 2px;
                padding-bottom: 2px;
                border-bottom: 2px solid #eef3ff;
            }
        """)
        self.resultsLayout.addWidget(resultsTitle)
        
        # 表格控件
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(["序号", "文件", "状态", "置信度", "坐标"])
        
        # 表格样式
        self.tableWidget.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                color: #2d3748;
                gridline-color: #e0ecfd;
                border-radius: 10px;
                font-size: 14px;
                padding: 5px;
                border: 1px solid #e6edff;
                selection-background-color: #d6e3ff;
                selection-color: #2d3748;
            }
            QHeaderView::section {
                background-color: #4a7bff;
                color: white;
                padding: 12px 15px;
                font-weight: bold;
                font-size: 15px;
                border: none;
            }
            QTableWidget::item {
                padding: 12px 15px;
                border-bottom: 1px solid #f0f4ff;
            }
            QTableCornerButton::section {
                background-color: #4a7bff;
                border-radius: 4px 0 0 0;
            }
            /* 自定义滚动条样式 */
            QScrollBar:vertical {
                width: 12px;
                background: #f0f0f0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #a0a0a0;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # 表格设置
        self.tableWidget.horizontalHeader().setHighlightSections(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setDefaultSectionSize(40)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        
        # 设置初始列宽比例
        self.tableWidget.setColumnWidth(0, 60)    # 序号列窄些
        self.tableWidget.setColumnWidth(1, 200)   # 行为类型稍宽
        self.tableWidget.setColumnWidth(2, 250)   # 位置坐标
        self.tableWidget.setColumnWidth(3, 120)   # 置信度
        self.tableWidget.setColumnWidth(4, 180)   # 状态
        
        # 直接将表格添加到布局，不需要额外的滚动区域
        self.resultsLayout.addWidget(self.tableWidget)
        
        asrTitle = QtWidgets.QLabel("语音识别明细")
        asrTitle.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4a7bff;
                margin-top: 12px;
                margin-bottom: 2px;
                padding-bottom: 2px;
                border-bottom: 2px solid #eef3ff;
            }
        """)
        self.resultsLayout.addWidget(asrTitle)
        
        self.asrTableWidget = QtWidgets.QTableWidget()
        self.asrTableWidget.setColumnCount(3)
        self.asrTableWidget.setRowCount(0)
        self.asrTableWidget.setHorizontalHeaderLabels(["序号", "时间范围", "识别文本"])
        self.asrTableWidget.setMinimumHeight(220)
        self.asrTableWidget.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                color: #2d3748;
                gridline-color: #e0ecfd;
                border-radius: 10px;
                font-size: 14px;
                padding: 5px;
                border: 1px solid #e6edff;
                selection-background-color: #d6e3ff;
                selection-color: #2d3748;
            }
            QHeaderView::section {
                background-color: #4a7bff;
                color: white;
                padding: 12px 15px;
                font-weight: bold;
                font-size: 15px;
                border: none;
            }
            QTableWidget::item {
                padding: 12px 15px;
                border-bottom: 1px solid #f0f4ff;
            }
            QTableCornerButton::section {
                background-color: #4a7bff;
                border-radius: 4px 0 0 0;
            }
        """)
        self.asrTableWidget.horizontalHeader().setHighlightSections(False)
        self.asrTableWidget.verticalHeader().setVisible(False)
        self.asrTableWidget.verticalHeader().setDefaultSectionSize(40)
        self.asrTableWidget.setAlternatingRowColors(True)
        self.asrTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.asrTableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.asrTableWidget.setColumnWidth(0, 60)
        self.asrTableWidget.setColumnWidth(1, 180)
        self.asrTableWidget.setColumnWidth(2, 700)
        self.resultsLayout.addWidget(self.asrTableWidget)
        self.resultsLayout.setStretch(self.resultsLayout.indexOf(resultsTitle), 0)
        self.resultsLayout.setStretch(self.resultsLayout.indexOf(self.tableWidget), 1)
        self.resultsLayout.setStretch(self.resultsLayout.indexOf(asrTitle), 0)
        self.resultsLayout.setStretch(self.resultsLayout.indexOf(self.asrTableWidget), 1)
        
        # 添加到中间布局
        self.middleLayout.addWidget(self.resultsCard)
        
        # 右侧控制面板
        self.controlPanel = QtWidgets.QFrame(self.centralwidget)
        self.controlPanel.setMinimumWidth(350)
        self.controlPanel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 16px;
                border: none;
            }
        """)
        
        # 使用垂直布局，并设置尺寸约束
        self.controlLayout = QtWidgets.QVBoxLayout(self.controlPanel)
        self.controlLayout.setContentsMargins(25, 25, 25, 25)
        self.controlLayout.setSpacing(20)
        self.controlPanel.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        
        # 面板标题
        panelTitle = QtWidgets.QLabel("目标检测控制面板")
        panelTitle.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4a7bff;
                padding-bottom: 5px;
                border-bottom: 2px solid #eef3ff;
            }
        """)
        self.controlLayout.addWidget(panelTitle)
        
        # 目标设定标题
        targetTitle = QtWidgets.QLabel("目标设定")
        targetTitle.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 600;
                color: #4a7bff;
                margin-bottom: 3px;
            }
        """)
        self.controlLayout.addWidget(targetTitle)
        
        # 监控范围选择 - 使用网格布局更好地管理大小
        rangeLayout = QtWidgets.QGridLayout()
        
        rangeLabel = QtWidgets.QLabel("监控范围:")
        rangeLabel.setStyleSheet("font-size: 14px; color: #555; font-weight: 500;")
        rangeLayout.addWidget(rangeLabel, 0, 0)
        
        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItems(["请先选择图片或视频！"])
        self.comboBox.setFixedHeight(45)
        self.comboBox.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #333;
                border: 2px solid #d1e0fe;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 15px;
                font-weight: 500;
            }
            QComboBox:hover {
                border-color: #4a7bff;
            }
            QComboBox:focus {
                border-color: #4a7bff;
            }
            QComboBox::drop-down {
                border: none;
                width: 40px;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #d1e0fe;
                selection-background-color: #d6e3ff;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                margin-top: 8px;
            }
        """)
        rangeLayout.addWidget(self.comboBox, 0, 1)
        
        self.controlLayout.addLayout(rangeLayout)
        
        # 关注行为选择
        behaviorLayout = QtWidgets.QGridLayout()
        
        behaviorLabel = QtWidgets.QLabel("关注行为:")
        behaviorLabel.setStyleSheet("font-size: 14px; color: #555; font-weight: 500;")
        behaviorLayout.addWidget(behaviorLabel, 0, 0)
        
        self.behaviorComboBox = QtWidgets.QComboBox()
        self.behaviorComboBox.addItems(["所有行为"])
        self.behaviorComboBox.setFixedHeight(45)
        self.behaviorComboBox.setStyleSheet("""
            QComboBox {
                background-color: #ffffff;
                color: #333;
                border: 2px solid #d1e0fe;
                border-radius: 10px;
                padding: 12px 15px;
                font-size: 15px;
                font-weight: 500;
            }
            QComboBox:hover {
                border-color: #4a7bff;
            }
            QComboBox:focus {
                border-color: #4a7bff;
            }
            QComboBox::drop-down {
                border: none;
                width: 115px;
                padding-right: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #d1e0fe;
                selection-background-color: #d6e3ff;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                margin-top: 8px;
            }
        """)
        behaviorLayout.addWidget(self.behaviorComboBox, 0, 1)
        self.controlLayout.addLayout(behaviorLayout)
        
        # （已移除语音识别相关控件）
        
        
        
        # 退出按钮 - 设置固定高度
        self.ExitBtn = QtWidgets.QPushButton("退出系统")
        self.ExitBtn.setFixedHeight(55)
        self.ExitBtn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #ff4d4f;
                border: 2px solid #ff4d4f;
                border-radius: 10px;
                padding: 14px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #fff2f0;
            }
            QPushButton:pressed {
                background-color: #ffccc7;
            }
        """)
        self.ExitBtn.setIcon(QtGui.QIcon(":/icons/ui_imgs/icons/退出.png"))
        self.ExitBtn.setIconSize(QtCore.QSize(28, 28))
        self.controlLayout.addWidget(self.ExitBtn)
        
        self.middleLayout.addWidget(self.controlPanel)
        self.verticalLayout.addLayout(self.middleLayout)
        
        # === 底部区域: 居中操作按钮 ===
        # 按钮容器 - 用于居中按钮
        self.buttonContainer = QtWidgets.QWidget(self.centralwidget)
        self.buttonContainer.setMaximumHeight(100)
        self.buttonContainer.setStyleSheet("background: transparent;")
        
        self.buttonLayout = QtWidgets.QHBoxLayout(self.buttonContainer)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.addStretch(1)  # 左侧弹性空间
        
        # 按钮组容器
        self.buttonGroup = QtWidgets.QWidget()
        self.buttonGroup.setStyleSheet("background: transparent;")
        self.groupLayout = QtWidgets.QHBoxLayout(self.buttonGroup)
        self.groupLayout.setSpacing(30)
        self.groupLayout.setContentsMargins(0, 0, 0, 0)
        
        # 图片导入按钮
        self.PicBtn = QtWidgets.QPushButton("图片检测")
        self.PicBtn.setIcon(QtGui.QIcon(":/icons/ui_imgs/icons/img.png"))
        self.PicBtn.setIconSize(QtCore.QSize(32, 32))
        self.PicBtn.setFixedSize(180, 60)  # 使用固定尺寸防止变形
        self.PicBtn.setStyleSheet("""
            QPushButton {
                background-color: #4a7bff;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5d8eff;
            }
            QPushButton:pressed {
                background-color: #3a6ae3;
            }
        """)
        self.groupLayout.addWidget(self.PicBtn)
        
        # 视频导入按钮
        self.VideoBtn = QtWidgets.QPushButton("视频检测")
        self.VideoBtn.setIcon(QtGui.QIcon(":/icons/ui_imgs/icons/video.png"))
        self.VideoBtn.setIconSize(QtCore.QSize(32, 32))
        self.VideoBtn.setFixedSize(180, 60)
        self.VideoBtn.setStyleSheet("""
            QPushButton {
                background-color: #805ad5;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9f7aea;
            }
            QPushButton:pressed {
                background-color: #6b46c1;
            }
        """)
        self.groupLayout.addWidget(self.VideoBtn)
        
        # 摄像头按钮
        self.CapBtn = QtWidgets.QPushButton("实时监控")
        self.CapBtn.setIcon(QtGui.QIcon(":/icons/ui_imgs/icons/camera.png"))
        self.CapBtn.setIconSize(QtCore.QSize(32, 32))
        self.CapBtn.setFixedSize(180, 60)
        self.CapBtn.setStyleSheet("""
            QPushButton {
                background-color: #0bc5ea;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00c7de;
            }
            QPushButton:pressed {
                background-color: #00a3c4;
            }
        """)
        self.groupLayout.addWidget(self.CapBtn)
        
        # 新增的导出按钮
        self.ExportBtn = QtWidgets.QPushButton("导出结果")
        self.ExportBtn.setIcon(QtGui.QIcon(":/icons/ui_imgs/icons/导出.png"))  # 需要准备一个导出图标
        self.ExportBtn.setIconSize(QtCore.QSize(32, 32))
        self.ExportBtn.setFixedSize(180, 60)
        self.ExportBtn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34d399;
            }
            QPushButton:pressed {
                background-color: #059669;
            }
        """)
        self.groupLayout.addWidget(self.ExportBtn)
        
        self.buttonLayout.addWidget(self.buttonGroup)
        self.buttonLayout.addStretch(1)  # 右侧弹性空间

        self.buttonLayout.addWidget(self.buttonGroup)
        self.buttonLayout.addStretch(1)  # 右侧弹性空间
        self.verticalLayout.addWidget(self.buttonContainer)
        
        # 设置中央控件
        MainWindow.setCentralWidget(self.centralwidget)
        
        # 状态栏
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #ffffff;
                color: #718096;
                border-top: 1px solid #e8ecff;
                font-size: 12px;
                padding: 5px 15px;
            }
        """)
        MainWindow.setStatusBar(self.statusbar)
        
        # 连接UI元素
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
