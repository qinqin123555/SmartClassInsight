<template>
  <Sidebar>
    <div class="panel">
      <h3>图像检测</h3>
      <div class="row">
        <input type="file" @change="onFile" accept="image/*" />
        <button :disabled="loading || !file" @click="start">{{ loading ? '检测中...' : '开始检测' }}</button>
      </div>
      
      <!-- 原图预览 -->
      <div v-if="previewUrl" class="preview-section">
        <h4>原图</h4>
        <div class="preview-wrap">
          <img :src="previewUrl" alt="预览图" class="preview" />
        </div>
      </div>
      
      <!-- 检测结果图片 -->
      <div v-if="annotatedImageUrl" class="preview-section">
        <h4>检测结果</h4>
        <div class="preview-wrap">
          <img :src="annotatedImageUrl" alt="检测结果" class="preview annotated" />
        </div>
        <div class="download-row">
          <a :href="annotatedImageUrl" :download="'detected-' + (file?.name || 'result.jpg')" class="download-btn">
            下载检测结果图片
          </a>
        </div>
      </div>
      
      <!-- 检测详情 -->
      <div v-if="detections.length > 0" class="detections-section">
        <h4>检测详情</h4>
        <table class="detections-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>行为</th>
              <th>置信度</th>
              <th>位置</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(det, index) in detections" :key="index">
              <td>{{ index + 1 }}</td>
              <td>{{ det.class }}</td>
              <td>{{ (det.confidence * 100).toFixed(2) }}%</td>
              <td>[{{ det.bbox.map(v => Math.round(v)).join(', ') }}]</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="result" class="result">
        <div class="pill" v-if="engine">{{ engine === 'python' ? 'Python' : '回退' }}</div>
        <div class="title">{{ result }}</div>
        <div class="meta" v-if="count !== null">检测到 {{ count }} 个目标</div>
      </div>
    </div>
  </Sidebar>
</template>

<script setup>
import Sidebar from '../components/Sidebar.vue'
import axios from 'axios'
import { ref } from 'vue'

const file = ref(null)
const loading = ref(false)
const error = ref('')
const result = ref('')
const count = ref(null)
const engine = ref('')
const previewUrl = ref('')
const annotatedImageUrl = ref('')
const detections = ref([])

const onFile = (e) => {
  error.value = ''
  engine.value = ''
  result.value = ''
  annotatedImageUrl.value = ''
  detections.value = []
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  file.value = e.target.files && e.target.files[0] ? e.target.files[0] : null
  previewUrl.value = file.value ? URL.createObjectURL(file.value) : ''
}

const start = async () => {
  if (!file.value) return
  try {
    loading.value = true
    error.value = ''
    annotatedImageUrl.value = ''
    detections.value = []
    
    const fd = new FormData()
    fd.append('file', file.value)
    
    const { data } = await axios.post('/api/detect/image/python', fd)
    
    if (data && data.ok) {
      result.value = data.resultText
      count.value = typeof data.count === 'number' ? data.count : null
      engine.value = data.engine || ''
      
      // 显示标注后的图片
      if (data.annotatedImage) {
        annotatedImageUrl.value = data.annotatedImage
      }
      
      // 显示检测详情
      if (data.detections && Array.isArray(data.detections)) {
        detections.value = data.detections
      }
    } else {
      error.value = 'Python检测不可用或返回异常'
    }
  } catch (e) {
    error.value = 'Python检测不可用或网络异常: ' + (e.message || '')
  } finally {
    loading.value = false
  }
}
</script>

<style>
.panel { background: #fff; border-radius: 10px; padding: 18px; }
.row { display: flex; gap: 8px; align-items: center; flex-wrap: nowrap; }
.row input[type="file"] { max-width: 360px; }
.row button { white-space: nowrap; }

.preview-section { margin-top: 16px; }
.preview-section h4 { margin: 0 0 8px 0; color: #374151; font-size: 14px; }
.preview-wrap { margin-top: 8px; }
.preview { display: block; max-width: 520px; width: 100%; height: auto; border-radius: 10px; border: 1px solid #e5e7eb; box-shadow: var(--shadow); background: #f9fafb; }
.preview.annotated { border: 2px solid #3b82f6; }

.download-row { margin-top: 12px; }
.download-btn { display: inline-block; background: #3b82f6; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 14px; }
.download-btn:hover { background: #2563eb; }

.detections-section { margin-top: 16px; }
.detections-section h4 { margin: 0 0 8px 0; color: #374151; font-size: 14px; }
.detections-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.detections-table th, .detections-table td { border: 1px solid #e5e7eb; padding: 8px 12px; text-align: left; }
.detections-table th { background: #f9fafb; font-weight: 600; }
.detections-table tr:nth-child(even) { background: #f9fafb; }

.error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; border-radius: 8px; padding: 10px 12px; margin-top: 12px; }
.result { position: relative; background: #ffffff; color: var(--text); border: 1px solid #e5e7eb; border-radius: 14px; padding: 14px; margin-top: 12px; box-shadow: var(--shadow); }
.result .pill { position: absolute; right: 12px; top: 12px; background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; border-radius: 999px; font-size: 12px; padding: 4px 8px; }
.result .title { font-size: 22px; font-weight: 700; color: var(--primary); }
.result .meta { margin-top: 4px; font-size: 13px; color: #6b7280; }
</style>
