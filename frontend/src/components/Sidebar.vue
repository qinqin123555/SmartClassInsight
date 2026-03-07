<template>
  <div class="layout">
    <aside class="sidebar">
      <h2 class="title">智慧课堂</h2>
      <nav>
        <a :class="['navlink', isActive('/home') ? 'active' : '']" @click="go('/home')">首页</a>
        <a :class="['navlink', isActive('/image-detect') ? 'active' : '']" @click="go('/image-detect')">图像检测</a>
        <a :class="['navlink', isActive('/video-detect') ? 'active' : '']" @click="go('/video-detect')">视频检测</a>
        <a :class="['navlink', isActive('/camera-detect') ? 'active' : '']" @click="go('/camera-detect')">摄像检测</a>
        <a :class="['navlink', isActive('/image-records') ? 'active' : '']" @click="go('/image-records')">图片识别记录</a>
        <a :class="['navlink', isActive('/video-records') ? 'active' : '']" @click="go('/video-records')">视频识别记录</a>
        <a :class="['navlink', isActive('/users') ? 'active' : '']" @click="go('/users')">用户管理</a>
        <a :class="['navlink', isActive('/profile') ? 'active' : '']" @click="go('/profile')">个人中心</a>
      </nav>
    </aside>
    <main class="content">
      <div class="topbar">
        <div class="user" @click="open = !open">
          <div class="avatar">{{ initials }}</div>
          <span class="uname">{{ uname }}</span>
          <div class="menu" v-if="open">
            <a @click="go('/profile')">个人中心</a>
            <a @click="logout">退出登录</a>
          </div>
        </div>
      </div>
      <div class="content-body">
        <slot />
      </div>
    </main>
  </div>
 </template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref, computed } from 'vue'
const router = useRouter()
const route = useRoute()
const go = (p) => router.push(p)
const isActive = (p) => route.path === p || route.path.startsWith(p)
const uname = ref(localStorage.getItem('username') || '用户')
const initials = computed(() => uname.value ? uname.value[0].toUpperCase() : 'U')
const open = ref(false)
const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style>
.layout { display: flex; height: 100%; }
.sidebar { width: 240px; background: linear-gradient(180deg, #eaf3ff, #dbeafe); color: #0f172a; padding: 20px; box-sizing: border-box; border-right: 1px solid var(--border); }
.sidebar .title { font-size: 18px; margin: 0 0 16px 0; color: var(--primary); }
.sidebar .navlink { display: block; color: #1f2937; text-decoration: none; padding: 10px 12px; border-radius: 10px; margin-bottom: 8px; border: 1px solid transparent; transition: all .2s ease; position: relative; }
.sidebar .navlink:hover { background: #ffffff; border-color: var(--border); box-shadow: var(--shadow); transform: translateY(-1px); }
.sidebar .navlink.active { background: #ffffff; border-color: var(--primary); box-shadow: var(--shadow); color: var(--primary); }
.sidebar .navlink.active::before { content: ''; position: absolute; left: -8px; top: 10px; bottom: 10px; width: 4px; background: var(--primary); border-radius: 4px; }
.content { flex: 1; background: var(--bg); padding: 8px 10px 12px; box-sizing: border-box; overflow: hidden; }
.topbar { display: flex; justify-content: flex-end; align-items: center; height: 56px; padding: 4px 0; }
.user { position: relative; display: flex; align-items: center; gap: 8px; cursor: pointer; }
.avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--primary); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; }
.uname { color: var(--text); }
.menu { position: absolute; right: 0; top: 42px; background: #fff; border: 1px solid var(--border); border-radius: 10px; box-shadow: var(--shadow); padding: 6px; min-width: 140px; z-index: 10; }
.menu a { display: block; padding: 8px 10px; color: var(--text); text-decoration: none; border-radius: 8px; }
.menu a:hover { background: #f3f7ff; color: var(--primary); }
.content-body { height: calc(100% - 56px); overflow: auto; }
</style>
