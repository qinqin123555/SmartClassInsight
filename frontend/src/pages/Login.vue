<template>
  <div class="login">
    <div class="brand">智慧课堂</div>
    <div class="subtitle">智能课堂行为分析平台</div>
    <div class="card">
      <div class="tabs">
        <button :class="['tab', !showRegister ? 'active' : '']" @click="showRegister=false">登录</button>
        <button :class="['tab', showRegister ? 'active' : '']" @click="showRegister=true">注册</button>
      </div>
      <div v-if="!showRegister">
        <h1>登录</h1>
        <input v-model="username" placeholder="用户名" />
        <input v-model="password" placeholder="密码" type="password" />
        <div v-if="loginError" class="error">{{ loginError }}</div>
        <button @click="doLogin">登录</button>
      </div>
      <div v-else>
        <h1>注册</h1>
        <input v-model="regUsername" placeholder="用户名" />
        <input v-model="regPassword" placeholder="密码" type="password" />
        <input v-model="regConfirm" placeholder="确认密码" type="password" />
        <div v-if="regError" class="error">{{ regError }}</div>
        <button :disabled="regLoading" @click="doRegister">{{ regLoading ? '注册中...' : '注册' }}</button>
        <div class="hint">已有账号？<a href="javascript:;" @click="showRegister=false">去登录</a></div>
      </div>
    </div>
    <div class="foot">© 智慧课堂 · 提升教学质量与课堂专注度</div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { useRouter } from 'vue-router'
import { ref } from 'vue'
const username = ref('')
const password = ref('')
const showRegister = ref(false)
const loginError = ref('')
const regUsername = ref('')
const regPassword = ref('')
const regConfirm = ref('')
const regLoading = ref(false)
const regError = ref('')
const router = useRouter()
const doLogin = async () => {
  loginError.value = ''
  try {
    const { data } = await axios.post('/api/auth/login', { username: username.value, password: password.value })
    localStorage.setItem('token', data.token)
    localStorage.setItem('username', data.username)
    router.push('/home')
  } catch (e) {
    if (e?.response?.status === 401) loginError.value = '用户名或密码错误'
    else loginError.value = '后端不可用或网络异常'
  }
}
const doRegister = async () => {
  regError.value = ''
  if (!regUsername.value || !regPassword.value || !regConfirm.value) {
    regError.value = '请填写所有字段'
    return
  }
  if (regPassword.value.length < 6) {
    regError.value = '密码至少6位'
    return
  }
  if (regPassword.value !== regConfirm.value) {
    regError.value = '两次密码不一致'
    return
  }
  try {
    regLoading.value = true
    const { data } = await axios.post('/api/auth/register', { username: regUsername.value, password: regPassword.value })
    if (data && data.ok) {
      username.value = regUsername.value
      password.value = regPassword.value
      showRegister.value = false
      const loginRes = await axios.post('/api/auth/login', { username: username.value, password: password.value })
      localStorage.setItem('token', loginRes.data.token)
      localStorage.setItem('username', loginRes.data.username)
      router.push('/home')
    } else {
      regError.value = '注册失败'
    }
  } catch (e) {
    const msg = e?.response?.data?.error
    if (msg === 'exists') regError.value = '用户名已存在'
    else if (msg === 'invalid') regError.value = '输入不合法'
    else regError.value = '后端不可用或网络异常'
  } finally {
    regLoading.value = false
  }
}
</script>

<style>
.login { position: relative; display: flex; flex-direction: column; height: 100%; align-items: center; justify-content: center; background: radial-gradient(1200px 600px at 20% 10%, #e0eeff 0%, rgba(224,238,255,0) 60%), radial-gradient(1000px 500px at 80% 90%, #d6e8ff 0%, rgba(214,232,255,0) 60%), linear-gradient(180deg, #edf5ff, #e6f0ff); }
.brand { font-size: 34px; font-weight: 800; color: var(--primary); margin-bottom: 8px; text-shadow: 0 8px 24px rgba(74,123,255,0.25); letter-spacing: 0.5px; }
.subtitle { margin-bottom: 18px; color: #6b7280; font-size: 14px; }
.card { position: relative; background: rgba(255,255,255,0.72); padding: 40px; border-radius: 24px; width: 66.6667vw; max-width: none; min-width: 760px; color: var(--text); border: 1px solid rgba(219,234,254,0.9); box-shadow: 0 32px 64px rgba(74,123,255,0.22); backdrop-filter: saturate(180%) blur(10px); }
.tabs { display: flex; gap: 8px; margin-bottom: 14px; background: #fff; padding: 6px; border-radius: 999px; border: 1px solid #dbeafe; }
.tab { flex: 1; background: #fff; color: var(--text); border: 1px solid transparent; border-radius: 999px; padding: 14px 0; font-size: 17px; transition: all .15s ease; }
.tab.active { background: linear-gradient(90deg, var(--primary), #60a5fa); color: #fff; box-shadow: 0 8px 16px rgba(74,123,255,0.25); }
.tab:active { background: var(--primary-dark); color: #fff; transform: translateY(1px); }
.tabs .tab { background: #fff; color: var(--text); border-color: #e8f0ff; }
.tabs .tab:hover { background: #ffffff; border-color: var(--border); box-shadow: var(--shadow); }
.tabs .tab.active { background: linear-gradient(90deg, var(--primary), #60a5fa); color: #fff; border-color: transparent; }
.card h1 { margin: 2px 0 20px 0; font-size: 26px; color: var(--primary); }
.card input { width: 100%; padding: 16px 18px; margin-bottom: 18px; border-radius: 16px; border: 1px solid var(--border); background: #f7fbff; color: var(--text); font-size: 17px; }
.card button { width: 100%; padding: 16px; background: linear-gradient(90deg, var(--primary), #60a5fa); border-color: transparent; font-size: 17px; }
.error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; border-radius: 10px; padding: 10px 12px; margin-bottom: 12px; }
.foot { margin-top: 16px; color: #6b7280; font-size: 12px; }
.hint { margin-top: 10px; text-align: center; color: #6b7280; }
.hint a { color: var(--primary); text-decoration: none; }
.hint a:hover { text-decoration: underline; }
@media (max-width: 720px) {
  .card { width: 92vw; padding: 26px; }
  .brand { font-size: 32px; }
  .card h1 { font-size: 24px; }
  .card input, .card button { font-size: 16px; padding: 14px; }
}
</style>
