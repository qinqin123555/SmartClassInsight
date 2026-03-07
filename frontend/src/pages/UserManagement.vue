<template>
  <Sidebar>
    <div class="panel">
      <h3>用户管理</h3>
      <table>
        <thead><tr><th>ID</th><th>用户名</th><th>角色</th></tr></thead>
        <tbody>
          <tr v-for="u in rows" :key="u.id">
            <td>{{ u.id }}</td><td>{{ u.username }}</td><td>{{ u.role }}</td>
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
  const { data } = await axios.get('/api/users')
  rows.value = data
})
</script>

<style>
.panel { background: #fff; border-radius: 10px; padding: 18px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: left; }
</style>
