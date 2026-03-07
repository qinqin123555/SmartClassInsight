import requests
import sys

def test_service():
    url = "http://localhost:5001"

    print("=" * 50)
    print("检测服务诊断工具")
    print("=" * 50)

    # 测试1: 健康检查
    print("\n[1] 测试健康检查接口...")
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✓ 服务正常运行")
            print(f"  响应: {response.json()}")
        else:
            print(f"✗ 服务返回错误状态码: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ 无法连接到服务 {url}")
        print(f"  请确认:")
        print(f"  1. Flask服务是否已启动 (运行 start_detect_service.bat)")
        print(f"  2. 端口5001是否被占用")
        return False
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False

    # 测试2: 检测接口
    print("\n[2] 测试检测接口...")
    print("  (需要上传图片文件进行完整测试)")

    print("\n" + "=" * 50)
    print("诊断完成")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_service()
    sys.exit(0 if success else 1)
