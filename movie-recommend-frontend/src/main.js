import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 导入Element Plus核心和样式（必须完整）
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 【重点】导入Element Plus提供的"所有图标"（避免漏导，适合新手）
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 创建Vue应用
const app = createApp(App)

// 1. 注册Element Plus和路由
app.use(ElementPlus)
app.use(router)

// 2. 注册所有Element Plus图标（全局可用，不用一个个写）
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 3. 挂载应用到页面
app.mount('#app')