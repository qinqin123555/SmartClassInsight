import sys

def test_asr_import():
    """测试ASR模块导入"""
    try:
        from asr_module import ASRModule, ASRIntegrator, ASRResult
        print("✓ ASR模块导入成功")
        return True
    except Exception as e:
        print(f"✗ ASR模块导入失败: {e}")
        return False

def test_asr_module():
    """测试ASR模块基本功能"""
    try:
        from asr_module import ASRModule
        
        # 创建ASR模块实例
        asr = ASRModule(language='zh-CN')
        print("✓ ASR模块实例创建成功")
        
        # 测试结果对象
        result = ASRResult("测试文本", 0.0, 5.0, 0.95)
        print(f"✓ ASR结果对象创建成功: {result}")
        
        # 测试依赖检查
        asr.check_dependencies()
        
        return True
    except Exception as e:
        print(f"✗ ASR模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_import():
    """测试主程序导入"""
    try:
        import Main
        print("✓ 主程序模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 主程序导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 50)
    print("ASR功能集成测试")
    print("=" * 50)
    
    results = []
    
    # 测试1: ASR模块导入
    print("\n[测试1] ASR模块导入测试")
    results.append(test_asr_import())
    
    # 测试2: ASR模块功能
    print("\n[测试2] ASR模块功能测试")
    results.append(test_asr_module())
    
    # 测试3: 主程序导入
    print("\n[测试3] 主程序导入测试")
    results.append(test_main_import())
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过")
        return 0
    else:
        print("✗ 部分测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())