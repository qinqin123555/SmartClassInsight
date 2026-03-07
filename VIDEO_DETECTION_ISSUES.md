# 视频检测问题记录

## 问题列表

### 1. 视频检测结果没有输出到前端页面

**问题描述**：
- 用户上传视频文件后，检测结果无法在前端页面显示
- 控制台报错：`Failed to fetch` 和 `net::ERR_ABORTED`

**原因分析**：
1. 前端SSE响应处理逻辑错误，没有正确处理以空行分隔的SSE事件格式
2. 后端SSE事件双重包装，导致格式错误
3. SseEmitter无法正确序列化Map对象

**解决方案**：
1. 修改前端代码，使用eventBuilder收集数据并在遇到"\n\n"时解析完整事件
2. 修改后端代码，解析Python服务返回的SSE事件，提取data部分并转换为Map对象
3. 使用ObjectMapper将Map对象显式转换为JSON字符串

**相关文件**：
- `frontend/src/pages/VideoDetect.vue`
- `backend/src/main/java/com/smartclassinsight/controller/DetectController.java`
- `backend/src/main/java/com/smartclassinsight/service/PythonDetectService.java`

---

### 2. 前端SSE响应处理逻辑错误

**问题描述**：
- 前端无法正确解析SSE事件
- SSE事件以空行分隔，但前端没有正确处理这种格式

**原因分析**：
前端代码没有正确处理SSE事件的分隔符"\n\n"，导致无法解析完整的事件数据。

**解决方案**：
修改前端代码，使用eventBuilder收集数据，并在遇到"\n\n"时解析完整事件：

```javascript
const newData = responseText.substring(buffer.length)
buffer = responseText

if (newData) {
  eventBuilder += newData
  
  // 处理完整的SSE事件
  let eventEndIndex
  while ((eventEndIndex = eventBuilder.indexOf('\n\n')) !== -1) {
    const eventData = eventBuilder.substring(0, eventEndIndex)
    eventBuilder = eventBuilder.substring(eventEndIndex + 2)
    
    // 解析SSE事件
    const lines = eventData.split('\n')
    let dataLine = ''
    
    for (const line of lines) {
      if (line.startsWith('data:')) {
        dataLine = line.substring(5)
      }
    }
    
    if (dataLine) {
      const data = JSON.parse(dataLine)
      // 处理数据...
    }
  }
}
```

**相关文件**：
- `frontend/src/pages/VideoDetect.vue`

---

### 3. 后端SSE事件双重包装

**问题描述**：
- 后端使用`emitter.send(sseLine)`直接发送完整SSE格式数据
- 导致SSE事件被双重包装，格式错误

**原因分析**：
Python服务返回的SSE响应已经包含了完整的SSE格式（包括"data:"前缀和"\n\n"后缀），后端直接转发导致双重包装。

**解决方案**：
修改后端代码，解析Python服务返回的SSE事件，提取data部分并转换为Map对象：

```java
private void parseAndForwardSseResponse(String sseResponse, VideoFrameCallback callback) {
  String[] lines = sseResponse.split("\n");
  String dataLine = null;
  
  for (String line : lines) {
    if (line.startsWith("data:")) {
      dataLine = line.substring(5);
    }
  }
  
  if (dataLine != null) {
    try {
      ObjectMapper mapper = new ObjectMapper();
      Map<String, Object> frameData = mapper.readValue(dataLine, new TypeReference<Map<String, Object>>() {});
      callback.onFrame(frameData);
    } catch (Exception e) {
      System.err.println("Error parsing SSE data: " + e.getMessage());
    }
  }
}
```

**相关文件**：
- `backend/src/main/java/com/smartclassinsight/service/PythonDetectService.java`

---

### 4. SseEmitter无法正确序列化Map对象

**问题描述**：
- SseEmitter无法正确序列化Map对象，导致数据格式错误

**原因分析**：
直接使用`SseEmitter.event().data(map)`发送Map对象时，SseEmitter的序列化机制可能无法正确处理。

**解决方案**：
使用ObjectMapper将Map对象显式转换为JSON字符串，然后构造标准SSE格式字符串发送：

```java
ObjectMapper mapper = new ObjectMapper();
String jsonData = mapper.writeValueAsString(frameData);
emitter.send(SseEmitter.event().data(jsonData));
```

**相关文件**：
- `backend/src/main/java/com/smartclassinsight/controller/DetectController.java`

---

### 5. 后端编译错误（VideoFrameCallback接口方法签名不匹配）

**问题描述**：
- 修改了PythonDetectService中VideoFrameCallback接口的onFrame方法参数类型
- 但未同步更新DetectController中的实现
- 导致编译错误

**原因分析**：
接口方法签名修改后，实现类的方法签名也需要相应修改。

**解决方案**：
更新DetectController中VideoFrameCallback接口的实现，将onFrame方法参数类型从String改为Map<String, Object>：

```java
@Override
public void onFrame(Map<String, Object> frameData) {
  try {
    ObjectMapper mapper = new ObjectMapper();
    String jsonData = mapper.writeValueAsString(frameData);
    emitter.send(SseEmitter.event().data(jsonData));
    
    frameDataHolder[0] = frameData;
    frameCount++;
    if (frameCount % 10 == 0) {
      System.out.println("Sent frame data: " + frameCount);
    }
  } catch (Exception e) {
    System.err.println("Error sending frame data: " + e.getMessage());
    e.printStackTrace();
  }
}
```

**相关文件**：
- `backend/src/main/java/com/smartclassinsight/controller/DetectController.java`

---

### 6. 后端编译错误（找不到符号ObjectMapper）

**问题描述**：
- 在PythonDetectService中使用ObjectMapper类但未导入相关包
- 导致编译错误

**原因分析**：
缺少Jackson库的导入语句。

**解决方案**：
添加Jackson库的导入语句：

```java
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.type.TypeReference;
```

**相关文件**：
- `backend/src/main/java/com/smartclassinsight/service/PythonDetectService.java`

---

### 7. 测试脚本无法解析SSE事件

**问题描述**：
- 测试脚本无法正确解析SSE事件
- SSE事件格式不正确，缺少正确的分隔符

**原因分析**：
SSE事件格式不正确，缺少正确的分隔符"\n\n"。

**解决方案**：
修改测试脚本，实现正确的SSE事件解析逻辑，按"\n\n"分隔符处理完整事件：

```python
buffer = ''
event_count = 0

for chunk in response.iter_content(chunk_size=8192):
    if chunk:
        chunk_str = chunk.decode('utf-8', errors='ignore')
        buffer += chunk_str
        
        # 处理完整的SSE事件
        while True:
            event_end = buffer.find('\n\n')
            if event_end == -1:
                break
            
            event_data = buffer[:event_end]
            buffer = buffer[event_end + 2:]
            
            event_count += 1
            
            # 解析SSE事件
            lines = event_data.split('\n')
            data_line = None
            
            for line in lines:
                if line.startswith('data:'):
                    data_line = line[5:]
            
            if data_line:
                data = json.loads(data_line)
                # 处理数据...
```

**相关文件**：
- `test_video_detection.py`
- `test_sse.py`
- `test_final.py`

---

### 8. SSE事件格式问题

**问题描述**：
- SseEmitter发送的数据格式不正确
- 第一个数据块只有5个字节，内容是`data:`
- 第二个数据块才包含完整的JSON数据

**原因分析**：
SseEmitter的缓存机制导致`data:`前缀和JSON数据分开发送。

**解决方案**：
使用`SseEmitter.event().data(jsonData)`方法发送数据，让SseEmitter自动添加`data:`前缀和`\n\n`后缀：

```java
ObjectMapper mapper = new ObjectMapper();
String jsonData = mapper.writeValueAsString(frameData);
emitter.send(SseEmitter.event().data(jsonData));
```

**相关文件**：
- `backend/src/main/java/com/smartclassinsight/controller/DetectController.java`

---

### 9. 原始视频没有显示到页面上

**问题描述**：
- 原始视频部分只有一个占位符，没有实际的视频播放器
- 用户上传视频后无法看到原始视频

**原因分析**：
前端代码没有添加视频播放器，只有一个占位符显示"检测中..."。

**解决方案**：
1. 添加视频URL计算属性：

```javascript
const videoUrl = computed(() => {
  if (!file.value) return ''
  return URL.createObjectURL(file.value)
})
```

2. 修改模板，添加HTML5视频播放器：

```html
<div class="video-box">
  <h4>原始视频</h4>
  <div v-if="!file" class="frame-placeholder">
    <span>请选择视频文件</span>
  </div>
  <video v-else :src="videoUrl" controls class="video-player"></video>
</div>
```

**相关文件**：
- `frontend/src/pages/VideoDetect.vue`

---

### 10. 前端SSE事件解析错误（data:前缀处理）

**问题描述**：
- 前端代码检查的是`data: `（带空格）
- 但后端发送的是`data:`（不带空格）
- 导致无法正确解析SSE事件

**原因分析**：
前端代码中的SSE事件解析逻辑与后端发送的数据格式不匹配。

**解决方案**：
修改前端代码，使其能够正确处理`data:`前缀（不带空格）：

```javascript
for (const line of lines) {
  if (line.startsWith('data:')) {
    dataLine = line.substring(5)  // 去掉'data:'前缀
  }
}
```

**相关文件**：
- `frontend/src/pages/VideoDetect.vue`

---

## 测试脚本

为了验证上述问题的修复，创建了多个测试脚本：

1. **test_simple.py**: 最小化测试脚本，验证基本API响应格式
2. **test_video_detection.py**: 主测试脚本，验证端到端视频检测流程
3. **test_sse.py**: SSE事件解析测试
4. **test_debug.py**: 调试脚本，详细输出SSE事件数据
5. **test_debug2.py**: 调试脚本，检查SSE事件分隔符
6. **test_final.py**: 最终测试脚本，验证完整的SSE事件处理

---

## 总结

通过以上问题的逐一解决，实现了以下功能：

1. ✅ 视频检测API端点
2. ✅ SSE（Server-Sent Events）实时数据流
3. ✅ 原始视频播放器
4. ✅ 检测结果实时显示
5. ✅ 前后端数据流处理

所有代码已提交到远程仓库：`https://github.com/qinqin123555/SmartClassInsight.git`

---

## 相关文档

- [DETECT_SERVICE.md](./DETECT_SERVICE.md) - Python检测服务说明文档
- [backend/README.md](./backend/README.md) - 后端服务说明文档
- [frontend/README.md](./frontend/README.md) - 前端应用说明文档
