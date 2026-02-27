import sys
import os

# 打印当前Python可执行文件
print(f"当前Python: {sys.executable}")

# 打印当前路径
print(f"当前路径: {os.getcwd()}")

# 移除可能的my_thesis路径
new_path = []
for path in sys.path:
    if 'my_thesis' not in path:
        new_path.append(path)
sys.path = new_path

print(f"修改后的路径: {sys.path}")

# 尝试导入必要的模块
try:
    import cv2
    print("✓ cv2导入成功")
except Exception as e:
    print(f"✗ cv2导入失败: {e}")
    sys.exit(1)

try:
    from PyQt5.QtWidgets import QApplication
    print("✓ PyQt5导入成功")
except Exception as e:
    print(f"✗ PyQt5导入失败: {e}")
    sys.exit(1)

try:
    from ultralytics import YOLO
    print("✓ ultralytics导入成功")
except Exception as e:
    print(f"✗ ultralytics导入失败: {e}")
    sys.exit(1)

# 运行Main.py
print("\n启动Main.py...")
import Main

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Main.MainWindow()
    win.show()
    sys.exit(app.exec_())