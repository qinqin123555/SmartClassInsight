import sys
import os

def test_dependencies():
    """测试依赖库"""
    print("\n[依赖检查]")
    
    deps = {
        'numpy': 'numpy',
        'cv2': 'opencv-python',
        'speech_recognition': 'SpeechRecognition',
        'moviepy': 'moviepy'
    }
    
    results = []
    for module, package in deps.items():
        try:
            __import__(module)
            print(f"✓ {package} 已安装")
            results.append(True)
        except ImportError:
            print(f"✗ {package} 未安装")
            results.append(False)
    
    return all(results)

def test_asr_module_core():
    """测试ASR模块核心功能（不依赖PyQt5）"""
    print("\n[ASR模块核心测试]")
    
    try:
        # 测试ASRResult类
        from asr_module import ASRResult
        
        result = ASRResult("测试文本", 0.0, 5.0, 0.95)
        print(f"✓ ASRResult对象创建成功")
        print(f"  文本: {result.text}")
        print(f"  时间范围: {result.start_time:.2f}s - {result.end_time:.2f}s")
        print(f"  置信度: {result.confidence}")
        
        return True
    except Exception as e:
        print(f"✗ ASR模块核心测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n[文件结构检查]")
    
    required_files = [
        'asr_module.py',
        'Main.py',
        'Config.py',
        'alltools.py'
    ]
    
    results = []
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename} 存在")
            results.append(True)
        else:
            print(f"✗ {filename} 不存在")
            results.append(False)
    
    return all(results)

def test_code_integration():
    """测试代码集成"""
    print("\n[代码集成检查]")
    
    try:
        # 检查Main.py是否导入了ASR模块
        with open('Main.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        checks = [
            ('ASR模块导入', 'from asr_module import ASRIntegrator'),
            ('ASR初始化', 'self.asr_integrator = ASRIntegrator()'),
            ('ASR结果存储', 'self.asr_results = []'),
            ('ASR显示更新', 'def update_asr_display'),
            ('ASR导出功能', 'self.asr_integrator.export_results')
        ]
        
        results = []
        for name, pattern in checks:
            if pattern in content:
                print(f"✓ {name} 已集成")
                results.append(True)
            else:
                print(f"✗ {name} 未找到")
                results.append(False)
        
        return all(results)
    except Exception as e:
        print(f"✗ 代码集成检查失败: {e}")
        return False

def main():
    print("=" * 60)
    print("ASR功能集成测试（简化版）")
    print("=" * 60)
    
    results = []
    
    # 测试1: 依赖检查
    results.append(test_dependencies())
    
    # 测试2: 文件结构
    results.append(test_file_structure())
    
    # 测试3: ASR模块核心功能
    results.append(test_asr_module_core())
    
    # 测试4: 代码集成
    results.append(test_code_integration())
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过！ASR功能已成功集成")
        print("\n下一步：")
        print("1. 安装PyQt5: pip install PyQt5")
        print("2. 安装PyAudio: pip install pyaudio")
        print("3. 运行主程序: python Main.py")
        return 0
    else:
        print("✗ 部分测试失败")
        print("\n请检查：")
        print("1. 是否安装了所有依赖库")
        print("2. 文件是否完整")
        print("3. 代码是否正确集成")
        return 1

if __name__ == "__main__":
    sys.exit(main())