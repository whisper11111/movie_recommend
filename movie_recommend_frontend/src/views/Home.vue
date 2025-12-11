<template>
  <div class="container">
    <!-- 系统介绍 -->
    <el-card class="mb-4" shadow="hover">
      <div class="card-content">
        <h2 style="margin-bottom: 10px; color: #409eff;">欢迎使用电影推荐系统</h2>
        <p style="line-height: 1.8; color: #666;">
          本系统基于协同过滤算法，为您推荐个性化的电影。您可以浏览电影列表、查看电影详情、对电影进行评分，
          系统会根据您的评分和浏览记录，推荐您可能喜欢的电影。
        </p>
        <div style="margin-top: 15px;">
          <el-button type="primary" @click="goToMovieList">浏览电影列表</el-button>
          <el-button v-if="isLogin" type="success" @click="goToRecommend">查看个性化推荐</el-button>
          <el-button v-else type="info" @click="goToLogin">登录后查看个性化推荐</el-button>
        </div>
      </div>
    </el-card>
    
    <!-- 热门电影 -->
    <el-card shadow="hover">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h3 style="color: #409eff;">热门电影推荐</h3>
        <el-link href="/movie/list">查看更多 →</el-link>
      </div>
      
      <!-- 热门电影列表（网格布局） -->
      <el-row :gutter="20">
        <el-col :span="6" v-for="movie in hotMovies" :key="movie.id">
          <el-card class="movie-card" @click="goToMovieDetail(movie.id)">
            <div style="height: 200px; background-color: #f5f5f5; display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
              <el-icon style="font-size: 30px; color: #ccc;"><VideoFilled /></el-icon>
              <span style="margin-left: 10px; color: #ccc;">电影海报</span>
            </div>
            <div class="card-body">
              <h4 style="margin-bottom: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ movie.name }}</h4>
              <p style="font-size: 12px; color: #666; margin-bottom: 5px;">导演：{{ movie.director }}</p>
              <p style="font-size: 12px; color: #666; margin-bottom: 5px;">类型：{{ movie.style }}</p>
              <div style="display: flex; align-items: center; color: #ff9f43;">
                <el-icon><StarFilled /></el-icon>
                <span style="margin-left: 5px;">{{ movie.avg_score }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

// 路由实例
const router = useRouter()

// 响应式数据：热门电影列表、登录状态
const hotMovies = ref([])
const isLogin = ref(false)
const userId = ref('')

// 页面加载时执行
onMounted(() => {
  // 检查登录状态
  const storedUserId = localStorage.getItem('userId')
  if (storedUserId) {
    isLogin.value = true
    userId.value = storedUserId
  }
  
  // 获取热门电影
  getHotMovies()
})

// 获取热门电影（调用后端接口）
const getHotMovies = async () => {
  try {
    // 后端接口地址：http://localhost:5000/api/movie/hot
    const response = await axios.get('http://localhost:5000/api/movie/hot', {
      params: { limit: 8 } // 取前8部热门电影
    })
    if (response.data.code === 1) {
      hotMovies.value = response.data.data
    } else {
      ElMessage.warning(response.data.msg)
    }
  } catch (error) {
    ElMessage.error('获取热门电影失败，请稍后再试')
    console.error('Error:', error)
  }
}

// 跳转到电影列表页
const goToMovieList = () => {
  router.push('/movie/list')
}

// 跳转到个性化推荐页
const goToRecommend = () => {
  router.push(`/recommend/${userId.value}`)
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

// 跳转到电影详情页
const goToMovieDetail = (movieId) => {
  router.push(`/movie/detail/${movieId}`)
}

// 导入Element Plus的消息提示组件
import { ElMessage } from 'element-plus'
</script>

<style scoped>
/* 卡片内容样式 */
.card-content {
  line-height: 1.8;
}

/* 电影卡片样式 */
.movie-card {
  cursor: pointer;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>