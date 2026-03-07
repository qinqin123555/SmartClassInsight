<template>
  <Sidebar>
    <div class="home">
    <div class="grid">
      <div class="card">
        <div class="label">累计服务次数</div>
        <div class="value">{{ summary.serviceCount }}</div>
      </div>
      <div class="card">
        <div class="label">检测结果最多阅读</div>
        <div class="value">{{ summary.mostReadTitle }}</div>
      </div>
      <div class="card">
        <div class="label">平均检测耗时</div>
        <div class="value">{{ summary.avgDetectionMs }} ms</div>
      </div>
      <div class="card">
        <div class="label">累计服务用户</div>
        <div class="value">{{ summary.userCount }}</div>
      </div>
    </div>
    <div class="days">
      <h3>最近5天检测数量</h3>
      <div class="bars">
        <div v-for="(n,i) in summary.last5DaysCounts" :key="i" class="bar">
          <div class="barfill" :style="{height: (n*4)+'px'}"></div>
          <div class="barlabel">{{ n }}</div>
        </div>
      </div>
    </div>
    </div>
  </Sidebar>
</template>

<script setup>
import axios from 'axios'
import { ref, onMounted } from 'vue'
import Sidebar from '../components/Sidebar.vue'
const summary = ref({ serviceCount: 0, mostReadTitle: '', avgDetectionMs: 0, userCount: 0, last5DaysCounts: [] })
onMounted(async () => {
  const { data } = await axios.get('/api/metrics/summary')
  summary.value = data
})
</script>

<style>
.home { width: 100%; margin: 0; padding: 6px 6px 10px; box-sizing: border-box; overflow: hidden; }
.grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px 14px; align-items: stretch; }
.card { background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 10px; box-shadow: var(--shadow); min-width: 0; }
.label { color: var(--muted); font-size: 14px; }
.value { font-size: 18px; font-weight: 600; margin-top: 6px; color: var(--text); }
.days { margin-top: 12px; background: var(--panel); border: 1px solid var(--border); border-radius: 14px; padding: 12px; box-shadow: var(--shadow); }
.days h3 { margin: 0 0 8px 0; font-size: 16px; color: var(--primary); }
.bars { display: flex; align-items: flex-end; gap: 8px; height: clamp(90px, 16vh, 130px); }
.bar { display: flex; flex-direction: column; align-items: center; }
.barfill { width: 26px; background: var(--primary); border-radius: 10px 10px 0 0; box-shadow: var(--shadow); }
.barlabel { margin-top: 8px; color: var(--text); }

@media (max-width: 768px) {
  .home { padding: 6px; }
  .grid { grid-template-columns: repeat(1, minmax(0, 1fr)); }
  .bars { height: 120px; }
}
@media (min-width: 769px) and (max-width: 1180px) {
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-height: 800px) {
  .card { padding: 10px; }
  .bars { height: 120px; }
}
</style>
