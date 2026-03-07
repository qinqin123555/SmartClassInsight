<template>
  <Sidebar>
    <div class="panel">
      <h3>个人中心</h3>
      <div class="item">用户名：{{ username }}</div>
      <div class="item">令牌：{{ token }}</div>
    </div>
  </Sidebar>
</template>

<script setup>
import Sidebar from '../components/Sidebar.vue'
const username = localStorage.getItem('username') || ''
const token = localStorage.getItem('token') || ''
</script>

<style>
.panel { background: #fff; border-radius: 10px; padding: 18px; }
.item { margin-bottom: 10px; }
</style>
