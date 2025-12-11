<template>
  <div class="container">
    <el-page-header content="个性化推荐" @back="goBack"></el-page-header>
    
    <!-- 推荐电影列表 -->
    <el-card shadow="hover" class="mt-4">
      <div style="margin-bottom: 20px;">
        <h3 style="color: #409eff;">为您推荐的电影</h3>
        <p style="color: #666; margin-top: 5px;">基于您的评分和相似用户的喜好生成</p>
      </div>
      
      <!-- 推荐电影网格 -->
      <el-row :gutter="20">
        <el-col :span="6" v-for="movie in recommendMovies" :key="movie.id">
          <el-card class="movie-card" @click="goToMovieDetail(movie.id)">
            <!-- 🔥 核心修复：海报渲染（Base64格式） -->
            <div style="height: 200px; margin-bottom: 10px; overflow: hidden; border-radius: 5px;">
              <el-image
                v-if="movie.picture"
                :src="`data:image/jpeg;base64,${movie.picture}`"
                style="width: 100%; height: 100%;"
                fit="cover"
                preview-src-list="['data:image/jpeg;base64,' + movie.picture]"
              >
                <!-- 加载失败时显示占位 -->
                <template #error>
                  <div style="width: 100%; height: 100%; background-color: #f5f5f5; display: flex; align-items: center; justify-content: center;">
                    <el-icon style="font-size: 30px; color: #ccc;"><VideoFilled /></el-icon>
                    <span style="margin-left: 10px; color: #ccc;">海报加载失败</span>
                  </div>
                </template>
              </el-image>
              <!-- 无海报时显示占位 -->
              <div v-else style="width: 100%; height: 100%; background-color: #f5f5f5; display: flex; align-items: center; justify-content: center;">
                <el-icon style="font-size: 30px; color: #ccc;"><VideoFilled /></el-icon>
                <span style="margin-left: 10px; color: #ccc;">电影海报</span>
              </div>
            </div>
            <div class="card-body">
              <h4 style="margin-bottom: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ movie.name || '未知电影' }}</h4>
              <p style="font-size: 12px; color: #666; margin-bottom: 5px;">导演：{{ movie.director || '未知' }}</p>
              <p style="font-size: 12px; color: #666; margin-bottom: 5px;">类型：{{ (movie.style || []).join('、') || '未知' }}</p>
              <div style="display: flex; align-items: center; color: #ff9f43;">
                <el-icon><StarFilled /></el-icon>
                <span style="margin-left: 5px;">{{ movie.avg_score || 0 }} ({{ movie.rating_count || 0 }}人评分)</span>
              </div>
              <p style="font-size: 12px; color: #666; margin-top: 5px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                简介：{{ movie.description || '暂无简介' }}
              </p>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 无推荐数据提示 -->
      <el-empty description="暂无推荐数据，可先去评分电影" v-if="recommendMovies.length === 0"></el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
// 🔥 修复：删除 VideoFilled 和 StarFilled 的导入
import { ElMessage, ElEmpty, ElPageHeader, ElImage, ElIcon } from 'element-plus'

// 路由实例和当前路由信息
const router = useRouter()
const route = useRoute()

// 响应式数据：推荐电影列表
const recommendMovies = ref([])

// 页面加载时获取推荐电影
onMounted(() => {
  // 获取当前用户ID（从路由参数中获取）
  const userId = route.params.userId
  if (userId) {
    getRecommendMovies(userId)
  } else {
    // 无用户ID，跳转到登录页
    ElMessage.warning('请先登录')
    router.push('/login')
  }
})

// 获取个性化推荐电影（调用后端协同过滤接口）
const getRecommendMovies = async (userId) => {
  try {
    const response = await axios.get(`http://localhost:5000/api/recommend/${userId}`)
    console.log('推荐电影接口返回：', response.data) // 🔥 新增调试日志，查看picture字段
    if (response.data.code === 1 || response.data.code === 0) {
      // 无论是否有评分记录，都显示返回的推荐数据（无评分时返回热门电影）
      recommendMovies.value = response.data.data || []
      // 显示提示消息
      ElMessage.info(response.data.msg)
    } else {
      ElMessage.warning(response.data.msg)
    }
  } catch (error) {
    ElMessage.error('获取推荐电影失败，请稍后再试')
    console.error('Error:', error)
  }
}

// 跳转到电影详情页
const goToMovieDetail = (movieId) => {
  // 添加浏览记录
  const userId = route.params.userId
  addHistory(userId, movieId)
  // 跳转页面
  router.push(`/movie/detail/${movieId}`)
}

// 添加浏览记录（调用后端接口）
const addHistory = async (userId, movieId) => {
  try {
    await axios.post('http://localhost:5000/api/user/history/add', {
      uid: parseInt(userId),
      mid: parseInt(movieId)
    })
  } catch (error) {
    console.error('添加浏览记录失败:', error)
  }
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
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

.el-page-header {
  margin-bottom: 10px;
}

/* 🔥 新增：修复图片预览层级 */
:deep(.el-image-viewer__wrapper) {
  z-index: 9999 !important;
}
</style>