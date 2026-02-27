"""
ASRResult类定义（独立版本，用于测试）
"""
class ASRResult:
    def __init__(self, text, start_time, end_time, confidence=0.0):
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.confidence = confidence
    
    def __str__(self):
        return f"[{self.start_time:.2f}s-{self.end_time:.2f}s] {self.text}"


def test_asr_result():
    """测试ASRResult类"""
    print("\n[ASRResult类测试]")
    
    try:
        # 创建ASRResult实例
        result = ASRResult("测试语音识别文本", 0.0, 5.0, 0.95)
        
        print(f"✓ ASRResult对象创建成功")
        print(f"  识别文本: {result.text}")
        print(f"  开始时间: {result.start_time:.2f}秒")
        print(f"  结束时间: {result.end_time:.2f}秒")
        print(f"  置信度: {result.confidence:.2f}")
        print(f"  字符串表示: {result}")
        
        # 测试属性访问
        assert result.text == "测试语音识别文本"
        assert result.start_time == 0.0
        assert result.end_time == 5.0
        assert result.confidence == 0.95
        
        print("✓ 所有属性验证通过")
        return True
        
    except Exception as e:
        print(f"✗ ASRResult类测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ASRResult类独立测试")
    print("=" * 60)
    
    if test_asr_result():
        print("\n✓ 测试通过")
    else:
        print("\n✗ 测试失败")