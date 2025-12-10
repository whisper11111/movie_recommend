// 路由配置：管理页面之间的跳转
import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import MovieList from '../views/MovieList.vue'
import MovieDetail from '../views/MovieDetail.vue'
import Recommend from '../views/Recommend.vue'

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
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由导航守卫：设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next() // 继续跳转
})

export default router