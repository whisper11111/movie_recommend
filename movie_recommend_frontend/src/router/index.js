// 路由配置：管理页面之间的跳转
import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios' // 新增：导入axios用于管理员权限验证

// 导入页面组件
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import MovieList from '../views/MovieList.vue'
import MovieDetail from '../views/MovieDetail.vue'
import Recommend from '../views/Recommend.vue'

import AdminLayout from '../layouts/AdminLayout.vue'  // 管理员布局组件
import UserManage from '../views/admin/UserManage.vue'
import MovieManage from '../views/admin/MovieManage.vue'

// 路由规则：path=访问路径，component=对应页面，name=路由名称
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: '电影推荐系统-首页' } // 页面标题
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '电影推荐系统-登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '电影推荐系统-注册' }
  },
  {
    path: '/movie/list',
    name: 'MovieList',
    component: MovieList,
    meta: { title: '电影推荐系统-电影列表' }
  },
  {
    path: '/movie/detail/:id', // 动态路由：/:id表示电影ID
    name: 'MovieDetail',
    component: MovieDetail,
    meta: { title: '电影推荐系统-电影详情' }
  },
  {
    path: '/recommend/:userId', // 动态路由：/:userId表示用户ID
    name: 'Recommend',
    component: Recommend,
    meta: { title: '电影推荐系统-个性化推荐' }
  },
  // 管理员路由（整合到路由列表里，注意逗号！）
  {
    path: '/admin',
    name: 'Admin',
    component: AdminLayout,
    meta: { 
      title: '电影推荐系统-管理员后台',
      requiresAdmin: true  // 标记需要管理员权限
    },
    children: [
      { 
        path: 'users', 
        name: 'UserManage', 
        component: UserManage,
        meta: { title: '电影推荐系统-用户管理' }
      },
      { 
        path: 'movies', 
        name: 'MovieManage', 
        component: MovieManage,
        meta: { title: '电影推荐系统-电影管理' }
      }
    ]
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 合并路由守卫（把标题设置和管理员权限验证写在同一个守卫里，避免重复）
router.beforeEach((to, from, next) => {
  // 1. 设置页面标题（保留你原来的功能）
  if (to.meta.title) {
    document.title = to.meta.title
  }

  // 2. 管理员权限验证（新增的功能）
  if (to.meta.requiresAdmin) {
    // 先判断用户是否登录（从本地存储拿userId）
    const userId = localStorage.getItem('userId')
    if (!userId) {
      // 没登录：跳转到登录页
      next('/login')
      return // 终止后续执行
    }

    // 已登录：调用后端接口验证是否为管理员
    axios.get('http://localhost:5000/api/user/is-admin', { 
      params: { uid: userId } // 传用户ID给后端
    })
    .then(res => {
      if (res.data.code === 1 && res.data.data.is_admin) {
        // 是管理员：允许进入后台
        next()
      } else {
        // 不是管理员：跳回首页
        next('/')
        alert('权限不足！仅管理员可访问后台')
      }
    })
    .catch(err => {
      // 接口调用失败：跳回首页
      console.error('验证管理员权限失败：', err)
      next('/')
      alert('验证权限失败，请重新登录')
    })
  } else {
    // 非管理员页面：直接放行
    next()
  }
})

export default router