<template>
  <Sidebar>
    <div class="panel">
      <h3>摄像检测</h3>
      <div class="row">
        <button>开启摄像头</button>
        <button>停止检测</button>
      </div>
    </div>
  </Sidebar>
</template>

<script setup>
import Sidebar from '../components/Sidebar.vue'
</script>

<style>
.panel { background: #fff; border-radius: 10px; padding: 18px; }
.row { display: flex; gap: 10px; }
</style>
