<template>
  <Sidebar>
    <div class="panel">
      <h3>视频检测</h3>
      <div class="row">
        <input type="file" @change="onFile" accept="video/*" />
        <button :disabled="loading || !file" @click="start">
          {{ loading ? '检测中...' : '开始检测' }}
        </button>
        <button v-if="loading" @click="stop" class="stop-btn">停止</button>
      </div>

      <!-- 进度条 -->
      <div v-if="loading && progress > 0" class="progress-section">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="progress-text">{{ progress.toFixed(1) }}%</div>
      </div>

      <!-- 视频播放区域 -->
      <div class="video-section" v-if="currentFrame || file">
        <div class="video-container">
          <!-- 原始视频 -->
          <div class="video-box">
            <h4>原始视频</h4>
            <div v-if="!file" class="frame-placeholder">
              <span>请选择视频文件</span>
            </div>
            <video v-else :src="videoUrl" controls class="video-player"></video>
          </div>

          <!-- 检测结果视频 -->
          <div class="video-box">
            <h4>检测结果</h4>
            <img v-if="currentFrame" :src="currentFrame" alt="检测结果" class="result-frame" />
            <div v-else class="frame-placeholder">
              <span>等待检测...</span>
            </div>
          </div>
        </div>

        <!-- 当前帧信息 -->
        <div v-if="currentFrameInfo" class="frame-info">
          <div class="info-item">
            <span class="label">帧号:</span>
            <span class="value">{{ currentFrameInfo.frame }} / {{ currentFrameInfo.totalFrames }}</span>
          </div>
          <div class="info-item">
            <span class="label">时间:</span>
            <span class="value">{{ currentFrameInfo.timestamp?.toFixed(2) }}s</span>
          </div>
          <div class="info-item">
            <span class="label">检测结果:</span>
            <span class="value result-badge" :class="getResultClass(currentFrameInfo.label)">
              {{ currentFrameInfo.label }}
            </span>
          </div>
          <div class="info-item">
            <span class="label">目标数量:</span>
            <span class="value">{{ currentFrameInfo.count }}</span>
          </div>
        </div>
      </div>

      <!-- 检测统计 -->
      <div v-if="detectionStats.length > 0" class="stats-section">
        <h4>检测统计</h4>
        <div class="stats-grid">
          <div v-for="(stat, index) in detectionStats" :key="index" class="stat-item">
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-count">{{ stat.count }} 次</div>
            <div class="stat-percentage">{{ stat.percentage }}%</div>
          </div>
        </div>
      </div>

      <!-- 检测详情表格 -->
      <div v-if="allDetections.length > 0" class="detections-section">
        <h4>检测详情 (最近10帧)</h4>
        <table class="detections-table">
          <thead>
            <tr>
              <th>帧号</th>
              <th>时间</th>
              <th>行为</th>
              <th>置信度</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(det, index) in recentDetections" :key="index">
              <td>{{ det.frame }}</td>
              <td>{{ det.timestamp?.toFixed(2) }}s</td>
              <td>{{ det.class }}</td>
              <td>{{ (det.confidence * 100).toFixed(2) }}%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </Sidebar>
</template>

<script setup>
import Sidebar from '../components/Sidebar.vue'
import { ref, computed } from 'vue'

const file = ref(null)
const loading = ref(false)
const error = ref('')
const currentFrame = ref('')
const currentFrameInfo = ref(null)
const progress = ref(0)
const allDetections = ref([])
const detectionStats = ref([])

const videoUrl = computed(() => {
  if (!file.value) return ''
  return URL.createObjectURL(file.value)
})

const recentDetections = computed(() => {
  return allDetections.value.slice(-10).reverse()
})

const onFile = (e) => {
  error.value = ''
  currentFrame.value = ''
  currentFrameInfo.value = null
  progress.value = 0
  allDetections.value = []
  detectionStats.value = []

  // 获取文件对象
  file.value = e.target.files && e.target.files[0] ? e.target.files[0] : null
  console.log('Selected file:', file.value)
  
  if (file.value) {
    console.log('File name:', file.value.name)
    console.log('File size:', file.value.size)
    console.log('File type:', file.value.type)
  }
}

const getResultClass = (label) => {
  const classMap = {
    '举手': 'raise-hand',
    '阅读': 'reading',
    '写作': 'writing',
    '使用手机': 'phone',
    '低头': 'head-down',
    '靠在桌子上': 'leaning',
    '无目标': 'no-target'
  }
  return classMap[label] || 'default'
}

const updateStats = () => {
  const stats = {}
  let total = 0

  allDetections.value.forEach(det => {
    const label = det.class
    if (!stats[label]) {
      stats[label] = 0
    }
    stats[label]++
    total++
  })

  detectionStats.value = Object.entries(stats).map(([label, count]) => ({
    label,
    count,
    percentage: total > 0 ? ((count / total) * 100).toFixed(1) : 0
  })).sort((a, b) => b.count - a.count)
}

const start = async () => {
  if (!file.value) return

  try {
    loading.value = true
    error.value = ''
    progress.value = 0
    allDetections.value = []
    
    // 测试后端连接
    try {
      console.log('Testing backend connection...')
      const testResponse = await fetch('/api/detect/health')
      console.log('Health check response:', testResponse.status)
      if (!testResponse.ok) {
        throw new Error('健康检查失败')
      }
      console.log('Backend connection successful')
    } catch (testError) {
      console.error('Health check failed:', testError)
      error.value = '无法连接到后端服务: ' + (testError.message || '')
      loading.value = false
      return
    }

    const formData = new FormData()
    console.log('Creating FormData...')
    console.log('File object:', file.value)
    console.log('File name:', file.value.name)
    console.log('File size:', file.value.size)
    console.log('File type:', file.value.type)
    
    formData.append('file', file.value)
    formData.append('skipFrames', '2')
    console.log('FormData created successfully')

    console.log('Preparing to send video detection request...')
    console.log('Request URL:', '/api/detect/video')
    console.log('Request method:', 'POST')

    // 使用XMLHttpRequest处理流式响应
    console.log('Sending XMLHttpRequest...')
    const xhr = new XMLHttpRequest()
    xhr.open('POST', '/api/detect/video', true)
    xhr.timeout = 60000 // 60秒超时
    xhr.responseType = 'text'
    
    let buffer = ''
    let frameCount = 0
    let eventBuilder = ''

    xhr.onreadystatechange = function() {
      console.log('XHR readyState:', xhr.readyState)
      console.log('XHR status:', xhr.status)
      
      // 当readyState为3或4时，处理响应数据
      if (xhr.readyState === 3 || xhr.readyState === 4) {
        try {
          const responseText = xhr.responseText
          console.log('XHR responseText length:', responseText.length)
          
          // 处理SSE响应
          const newData = responseText.substring(buffer.length)
          buffer = responseText
          
          if (newData) {
            console.log('New data received, length:', newData.length)
            eventBuilder += newData
            
            // 处理完整的SSE事件
            let eventEndIndex
            while ((eventEndIndex = eventBuilder.indexOf('\n\n')) !== -1) {
              const eventData = eventBuilder.substring(0, eventEndIndex)
              eventBuilder = eventBuilder.substring(eventEndIndex + 2)
              
              console.log('Processing complete event, length:', eventData.length)
              
              // 解析SSE事件
              const lines = eventData.split('\n')
              let dataLine = ''
              
              for (const line of lines) {
                if (line.startsWith('data:')) {
                  dataLine = line.substring(5)  // 去掉'data:'前缀
                }
              }
              
              if (dataLine) {
                try {
                  console.log('Attempting to parse JSON, data length:', dataLine.length)
                  const data = JSON.parse(dataLine)
                  
                  console.log('Received frame data:', {
                    frame: data.frame,
                    label: data.label,
                    count: data.count,
                    progress: data.progress
                  })

                  if (data.error) {
                    error.value = data.error
                    console.error('Error from server:', data.error)
                  }

                  // 更新当前帧
                  if (data.image) {
                    currentFrame.value = 'data:image/jpeg;base64,' + data.image
                    currentFrameInfo.value = {
                      frame: data.frame,
                      totalFrames: data.totalFrames,
                      timestamp: data.timestamp,
                      label: data.label,
                      count: data.count
                    }
                    progress.value = data.progress || 0
                    frameCount++

                    if (frameCount % 10 === 0) {
                      console.log(`Processed ${frameCount} frames`)
                    }

                    // 收集所有检测
                    if (data.detections) {
                      data.detections.forEach(det => {
                        allDetections.value.push({
                          frame: data.frame,
                          timestamp: data.timestamp,
                          ...det
                        })
                      })
                      updateStats()
                    }
                  }
                } catch (e) {
                  console.error('解析数据失败:', e)
                  console.error('Raw data length:', dataLine.length)
                  console.error('First 100 chars:', dataLine.substring(0, 100))
                }
              }
            }
          }
        } catch (e) {
          console.error('Error processing response:', e)
          console.error('Error stack:', e.stack)
        }
      }
      
      // 当readyState为4时，请求完成
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          console.log('XHR request completed successfully')
          console.log(`Video detection completed. Processed ${frameCount} frames`)
        } else {
          console.error('XHR request failed with status:', xhr.status)
          error.value = '检测请求失败: ' + xhr.status
        }
        loading.value = false
        console.log('Video detection process finished')
      }
    }

    xhr.onprogress = function(event) {
      if (event.lengthComputable) {
        const percentComplete = (event.loaded / event.total) * 100
        console.log('XHR progress:', percentComplete)
      }
    }

    xhr.onerror = function() {
      console.error('XHR error occurred')
      error.value = '网络错误: 无法连接到后端服务'
      loading.value = false
    }

    xhr.ontimeout = function() {
      console.error('XHR request timed out')
      error.value = '请求超时: 视频检测时间过长'
      loading.value = false
    }

    // 发送请求
    xhr.send(formData)
    console.log('XHR request sent')

  } catch (e) {
    console.error('Video detection error:', e)
    console.error('Error stack:', e.stack)
    error.value = '视频检测失败: ' + (e.message || '')
    loading.value = false
  }
}

const stop = () => {
  console.log('Stopping video detection...')
  loading.value = false
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }
}
</script>

<style>
.panel {
  background: #fff;
  border-radius: 10px;
  padding: 18px;
}

.row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.row input[type="file"] {
  max-width: 360px;
}

.stop-btn {
  background: #ef4444;
  color: white;
}

.stop-btn:hover {
  background: #dc2626;
}

/* 进度条 */
.progress-section {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 14px;
  color: #6b7280;
  min-width: 50px;
  text-align: right;
}

/* 视频区域 */
.video-section {
  margin-top: 20px;
}

.video-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.video-box {
  background: #f9fafb;
  border-radius: 10px;
  padding: 12px;
  border: 1px solid #e5e7eb;
}

.video-box h4 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 14px;
}

.video-player {
  width: 100%;
  height: auto;
  border-radius: 8px;
  background: #000;
}

.result-frame {
  width: 100%;
  height: auto;
  border-radius: 8px;
  border: 2px solid #3b82f6;
}

.frame-placeholder {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 8px;
  color: #9ca3af;
}

/* 帧信息 */
.frame-info {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px;
  background: #f9fafb;
  border-radius: 8px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item .label {
  color: #6b7280;
  font-size: 13px;
}

.info-item .value {
  color: #111827;
  font-weight: 600;
  font-size: 14px;
}

.result-badge {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.result-badge.raise-hand {
  background: #fee2e2;
  color: #991b1b;
}

.result-badge.reading {
  background: #dbeafe;
  color: #1e40af;
}

.result-badge.writing {
  background: #d1fae5;
  color: #065f46;
}

.result-badge.phone {
  background: #fef3c7;
  color: #92400e;
}

.result-badge.head-down {
  background: #fce7f3;
  color: #9d174d;
}

.result-badge.leaning {
  background: #e0e7ff;
  color: #3730a3;
}

.result-badge.no-target {
  background: #f3f4f6;
  color: #6b7280;
}

.result-badge.default {
  background: #e5e7eb;
  color: #374151;
}

/* 统计区域 */
.stats-section {
  margin-top: 20px;
}

.stats-section h4 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.stat-item {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-count {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.stat-percentage {
  font-size: 12px;
  color: #3b82f6;
  margin-top: 4px;
}

/* 检测详情表格 */
.detections-section {
  margin-top: 20px;
}

.detections-section h4 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 14px;
}

.detections-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.detections-table th,
.detections-table td {
  border: 1px solid #e5e7eb;
  padding: 8px 12px;
  text-align: left;
}

.detections-table th {
  background: #f9fafb;
  font-weight: 600;
}

.detections-table tr:nth-child(even) {
  background: #f9fafb;
}

.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 10px 12px;
  margin-top: 12px;
}

@media (max-width: 768px) {
  .video-container {
    grid-template-columns: 1fr;
  }
}
</style>