<template>
  <Sidebar>
    <div class="panel">
      <h3>视频识别记录</h3>
      <table>
        <thead><tr><th>ID</th><th>文件</th><th>结果</th><th>时间</th></tr></thead>
        <tbody>
          <tr v-for="r in rows" :key="r.id">
            <td>{{ r.id }}</td><td>{{ r.file }}</td><td>{{ r.result }}</td><td>{{ new Date(r.ts).toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </Sidebar>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'
import Sidebar from '../components/Sidebar.vue'
const rows = ref([])
onMounted(async () => {
  const { data } = await axios.get('/api/records/videos')
  rows.value = data
})
</script>

<style>
.panel { background: #fff; border-radius: 10px; padding: 18px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: left; }
</style>
