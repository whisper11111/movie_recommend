<template>
  <div class="container">
    <el-page-header content="电影列表" @back="goBack"></el-page-header>
    
    <!-- 电影列表 + 分页 -->
    <el-card shadow="hover" class="mt-4">
      <!-- 分页控件 -->
      <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[5, 10, 15]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
        ></el-pagination>
      </div>
      
      <!-- 电影网格 -->
      <el-row :gutter="20">
        <el-col :span="6" v-for="movie in movieList" :key="movie.id">
          <el-card class="movie-card" @click="goToMovieDetail(movie.id)">
            <!-- 海报渲染（Base64格式） -->
            <div style="height: 200px; margin-bottom: 10px; overflow: hidden;">
              <el-image
                v-if="movie.picture"
                :src="`data:image/jpeg;base64,${movie.picture}`"
                style="width: 100%; height: 100%;"
                fit="cover"
                preview-src-list="['data:image/jpeg;base64,' + movie.picture]"
              >
                <!-- 加载失败/异常时显示占位 -->
                <template #error>
                  <div style="height: 100%; background-color: #f5f5f5; display: flex; align-items: center; justify-content: center;">
                    <el-icon style="font-size: 30px; color: #ccc;"><VideoFilled /></el-icon>
                    <span style="margin-left: 10px; color: #ccc;">海报加载失败</span>
                  </div>
                </template>
              </el-image>
              <!-- 无海报时显示占位 -->
              <div v-else style="height: 100%; background-color: #f5f5f5; display: flex; align-items: center; justify-content: center;">
                <el-icon style="font-size: 30px; color: #ccc;"><VideoFilled /></el-icon>
                <span style="margin-left: 10px; color: #ccc;">电影海报</span>
              </div>
            </div>
            <div class="card-body">
              <h4 style="margin-bottom: 5px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{{ movie.name }}</h4>
              <p style="font-size: 12px; color: #666; margin-bottom: 5px;">导演：{{ movie.director || '未知' }}</p>
              <p style="font-size: 12px; color: #666; margin-bottom: 5px;">类型：{{ movie.style || '未知' }}</p>
              <p style="font-size: 12px; color: #666; margin-bottom: 5px;">上映时间：{{ movie.release_date || '未知' }}</p>
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
      
      <!-- 无数据提示 -->
      <el-empty description="暂无电影数据" v-if="movieList.length === 0"></el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { 
  ElMessage, ElEmpty, ElPagination, ElPageHeader, 
  ElImage, ElIcon, ElCard 
} from 'element-plus'

// 路由实例
const router = useRouter()

// 响应式数据：电影列表、分页参数
const movieList = ref([])
const currentPage = ref(1) // 当前页码
const pageSize = ref(10) // 每页条数
const total = ref(0) // 总电影数

// 页面加载时获取电影列表
onMounted(() => {
  getMovieList()
})

// 获取电影列表（调用后端接口）
const getMovieList = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/movie/list', {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    console.log('电影列表接口返回：', response.data) // 调试：查看picture字段是否有值
    if (response.data.code === 1) {
      movieList.value = response.data.data.movie_list || []
      total.value = response.data.data.total || 0
    } else {
      ElMessage.warning(response.data.msg || '获取数据失败')
    }
  } catch (error) {
    ElMessage.error('获取电影列表失败，请稍后再试')
    console.error('Error:', error)
  }
}

// 每页条数改变时触发
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1 // 重置为第一页
  getMovieList()
}

// 当前页码改变时触发
const handleCurrentChange = (val) => {
  currentPage.value = val
  getMovieList()
}

// 跳转到电影详情页
const goToMovieDetail = (movieId) => {
  // 如果用户已登录，添加浏览记录
  const userId = localStorage.getItem('userId')
  if (userId) {
    addHistory(userId, movieId)
  }
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
    // 无需提示，默默添加即可
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

/* 修复图片预览层级问题 */
:deep(.el-image-viewer__wrapper) {
  z-index: 9999 !important;
}

/* 适配响应式布局 */
@media (max-width: 1200px) {
  .el-col {
    --el-col-span: 8 !important;
  }
}

@media (max-width: 768px) {
  .el-col {
    --el-col-span: 12 !important;
  }
}
</style>