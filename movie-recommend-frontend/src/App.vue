<template>
  <div id="app">
    <!-- 导航栏：全局显示 -->
    <el-container style="min-height: 100vh;">
      <el-header style="background-color: #409eff; color: white;">
        <div class="container">
          <div style="display: flex; justify-content: space-between; align-items: center; height: 100%;">
            <!-- 左侧：系统名称 -->
            <el-link href="/" style="color: white; font-size: 20px; font-weight: bold;">
              电影推荐系统
            </el-link>
            
            <!-- 中间：导航菜单 -->
            <el-menu :default-active="activeMenu" mode="horizontal" background-color="transparent" text-color="white" active-text-color="white">
              <el-menu-item index="/">
                <el-icon><HomeFilled /></el-icon>
                <span>首页</span>
              </el-menu-item>
              <el-menu-item index="/movie/list">
                <el-icon><VideoFilled /></el-icon>
                <span>电影列表</span>
              </el-menu-item>
              <el-menu-item v-if="isLogin" :index="'/recommend/' + userId">
                <el-icon><StarFilled /></el-icon>
                <span>个性化推荐</span>
              </el-menu-item>
            </el-menu>
            
            <!-- 右侧：登录/注册/用户信息 -->
            <div style="display: flex; gap: 10px;">
              <el-link v-if="!isLogin" href="/login" style="color: white;">登录</el-link>
              <el-link v-if="!isLogin" href="/register" style="color: white;">注册</el-link>
              <el-dropdown v-if="isLogin" @command="handleDropdownCommand">
                <span class="el-dropdown-link" style="color: white; cursor: pointer; display: flex; align-items: center; gap: 5px;">
                  <el-icon><UserFilled /></el-icon>
                  {{ username }}
                  <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </el-header>
      
      <!-- 内容区：路由对应的页面会显示在这里 -->
      <el-main>
        <router-view />
      </el-main>
      
      <!-- 页脚 -->
      <el-footer style="text-align: center; padding: 20px; background-color: #f5f5f5;">
        <p>© 2025 电影推荐系统 - 基于协同过滤算法 - yule</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
// 导入需要的Vue工具和路由
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 路由实例（用于页面跳转）
const router = useRouter()

// 响应式数据：用户登录状态、用户名、用户ID
const isLogin = ref(false)
const username = ref('')
const userId = ref('')
// 导航菜单当前激活项（对应当前页面路径）
const activeMenu = ref('/')

// 页面加载时执行（刷新页面后保持登录状态）
onMounted(() => {
  // 从浏览器本地存储中获取登录信息
  const storedUserId = localStorage.getItem('userId')
  const storedUsername = localStorage.getItem('username')
  if (storedUserId && storedUsername) {
    isLogin.value = true
    userId.value = storedUserId
    username.value = storedUsername
  }
  
  // 设置当前导航菜单激活项（和当前页面路径匹配）
  activeMenu.value = router.currentRoute.value.path
})

// 监听路由变化，更新导航菜单激活项（切换页面时导航同步高亮）
router.afterEach((to) => {
  activeMenu.value = to.path
})

// 处理用户下拉菜单命令（只有"退出登录"功能）
const handleDropdownCommand = (command) => {
  if (command === 'logout') {
    // 退出登录：清除本地存储的登录信息
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    // 更新登录状态
    isLogin.value = false
    username.value = ''
    userId.value = ''
    // 跳转到首页
    router.push('/')
  }
}
</script>

<style scoped>
/* 导航栏样式：固定高度60px */
.el-header {
  height: 60px !important;
}

/* 导航菜单：去掉底部边框 */
.el-menu {
  border-bottom: none !important;
}

/* 用户下拉菜单链接样式 */
.el-dropdown-link {
  display: flex;
  align-items: center;
}

/* 页脚样式：灰色文字、居中对齐 */
.el-footer {
  color: #666;
  font-size: 14px;
}

/* 容器样式：页面内容居中 */
.container {
  width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
</style>