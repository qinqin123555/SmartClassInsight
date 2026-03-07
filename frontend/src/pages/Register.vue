<template>
  <div class="login">
    <div class="card">
      <h1>注册</h1>
      <input v-model="username" placeholder="用户名" />
      <input v-model="password" placeholder="密码" type="password" />
      <input v-model="confirm" placeholder="确认密码" type="password" />
      <button @click="doRegister">注册</button>
      <div style="margin-top:10px; text-align:center;">
        <a href="javascript:;" @click="goLogin" style="color:var(--primary)">已有账号？去登录</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ref } from 'vue'
const username = ref('')
const password = ref('')
const confirm = ref('')
const router = useRouter()
const doRegister = async () => {
  if (!username.value || !password.value || password.value !== confirm.value) return
  await axios.post('/api/auth/register', { username: username.value, password: password.value })
  router.push('/login')
}
const goLogin = () => router.push('/login')
</script>

<style>
.login { display: flex; height: 100%; align-items: center; justify-content: center; background: linear-gradient(180deg, #edf5ff, #e6f0ff); }
.card { background: var(--panel); padding: 24px; border-radius: 16px; width: 380px; color: var(--text); border: 1px solid var(--border); box-shadow: var(--shadow); }
.card h1 { margin: 0 0 16px 0; font-size: 22px; color: var(--primary); }
.card input { width: 100%; padding: 12px; margin-bottom: 14px; border-radius: 12px; border: 1px solid var(--border); background: #f7fbff; color: var(--text); }
.card button { width: 100%; padding: 12px; }
</style>
