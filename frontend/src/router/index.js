import { createRouter, createWebHistory } from 'vue-router'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Home from '../pages/Home.vue'
import ImageDetect from '../pages/ImageDetect.vue'
import VideoDetect from '../pages/VideoDetect.vue'
import CameraDetect from '../pages/CameraDetect.vue'
import ImageRecords from '../pages/ImageRecords.vue'
import VideoRecords from '../pages/VideoRecords.vue'
import UserManagement from '../pages/UserManagement.vue'
import Profile from '../pages/Profile.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/home', component: Home },
  { path: '/image-detect', component: ImageDetect },
  { path: '/video-detect', component: VideoDetect },
  { path: '/camera-detect', component: CameraDetect },
  { path: '/image-records', component: ImageRecords },
  { path: '/video-records', component: VideoRecords },
  { path: '/users', component: UserManagement },
  { path: '/profile', component: Profile }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
