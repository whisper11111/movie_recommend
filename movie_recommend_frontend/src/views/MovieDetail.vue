<template>
  <div class="container">
    <el-page-header content="电影详情" @back="goBack"></el-page-header>
    
    <el-card shadow="hover" class="mt-4" v-if="movieDetail.id">
      <!-- 电影基本信息 -->
      <div style="display: flex; gap: 30px; margin-bottom: 20px;">
        <!-- 🔥 核心修复：海报渲染（Base64格式） -->
        <div style="width: 200px; height: 300px; overflow: hidden; border-radius: 5px;">
          <el-image
            v-if="movieDetail.picture"
            :src="`data:image/jpeg;base64,${movieDetail.picture}`"
            style="width: 100%; height: 100%;"
            fit="cover"
            preview-src-list="['data:image/jpeg;base64,' + movieDetail.picture]"
          >
            <!-- 加载失败时显示占位 -->
            <template #error>
              <div style="width: 100%; height: 100%; background-color: #f5f5f5; display: flex; align-items: center; justify-content: center;">
                <el-icon style="font-size: 40px; color: #ccc;"><VideoFilled /></el-icon>
                <span style="margin-left: 10px; color: #ccc;">海报加载失败</span>
              </div>
            </template>
          </el-image>
          <!-- 无海报时显示占位 -->
          <div v-else style="width: 100%; height: 100%; background-color: #f5f5f5; display: flex; align-items: center; justify-content: center;">
            <el-icon style="font-size: 40px; color: #ccc;"><VideoFilled /></el-icon>
            <span style="margin-left: 10px; color: #ccc;">电影海报</span>
          </div>
        </div>
        
        <!-- 信息区域 -->
        <div style="flex: 1;">
          <h2 style="margin-bottom: 15px; color: #409eff;">{{ movieDetail.name || '未知电影' }}</h2>
          
          <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
            <div>
              <span style="color: #666; margin-right: 5px;">导演：</span>
              <span>{{ movieDetail.director || '未知' }}</span>
            </div>
            <div>
              <span style="color: #666; margin-right: 5px;">演员：</span>
              <span v-for="(actor, idx) in (movieDetail.actors || [])" :key="idx">{{ actor }}<span v-if="idx !== (movieDetail.actors.length - 1)">、</span></span>
              <span v-if="!movieDetail.actors || movieDetail.actors.length === 0">未知</span>
            </div>
            <div>
              <span style="color: #666; margin-right: 5px;">类型：</span>
              <span v-for="(style, idx) in (movieDetail.style || [])" :key="idx">
                <el-tag type="primary" size="small">{{ style }}</el-tag>
              </span>
              <span v-if="!movieDetail.style || movieDetail.style.length === 0">未知</span>
            </div>
            <div>
              <span style="color: #666; margin-right: 5px;">语言：</span>
              <span>{{ movieDetail.language || '未知' }}</span>
            </div>
            <div>
              <span style="color: #666; margin-right: 5px;">制片公司：</span>
              <span>{{ movieDetail.company || '未知' }}</span>
            </div>
            <div>
              <span style="color: #666; margin-right: 5px;">上映时间：</span>
              <span>{{ movieDetail.release_date || '未知' }}</span>
            </div>
            <div>
              <span style="color: #666; margin-right: 5px;">时长：</span>
              <span>{{ movieDetail.duration || '未知' }}</span>
            </div>
            <div>
              <span style="color: #666; margin-right: 5px;">评分：</span>
              <span style="color: #ff9f43; font-size: 18px; font-weight: bold;">{{ movieDetail.avg_score || 0 }}</span>
              <span style="color: #666; margin-left: 5px;">({{ movieDetail.rating_count || 0 }}人评分)</span>
            </div>
          </div>
          
          <!-- 评分按钮（仅登录用户可见） -->
          <el-button 
            type="primary" 
            @click="showRatingDialog = true" 
            v-if="isLogin && !hasRated"
          >
            <el-icon><StarFilled /></el-icon>
            我要评分
          </el-button>
          <el-button 
            type="success" 
            disabled 
            v-if="isLogin && hasRated"
          >
            <el-icon><StarFilled /></el-icon>
            已评分
          </el-button>
        </div>
      </div>
      
      <!-- 电影简介 -->
      <div style="margin-top: 20px;">
        <h3 style="margin-bottom: 10px; color: #409eff;">电影简介</h3>
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; line-height: 1.8;">
          {{ movieDetail.description || '暂无简介' }}
        </div>
      </div>
    </el-card>
    
    <!-- 无数据提示 -->
    <el-empty description="未找到该电影" v-else></el-empty>
    
    <!-- 评分弹窗 -->
    <el-dialog
      title="为电影评分"
      v-model="showRatingDialog"
      width="400px"
      :before-close="handleDialogClose"
    >
      <el-form :model="ratingForm" :rules="ratingRules" ref="ratingFormRef" label-width="80px">
        <el-form-item label="评分" prop="score">
          <el-rate v-model="ratingForm.score" :max="5" :precision="0.5" allow-half />
        </el-form-item>
        <el-form-item label="评论" prop="description">
          <el-input 
            v-model="ratingForm.description" 
            type="textarea" 
            placeholder="请输入您的评论（可选）" 
            rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRatingDialog = false">取消</el-button>
          <el-button type="primary" @click="handleRating">提交评分</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
// 🔥 修复：删除 VideoFilled 和 StarFilled 的导入
import { ElMessage, ElEmpty, ElPageHeader, ElTag, ElDialog, ElForm, ElFormItem, ElRate, ElInput, ElButton, ElImage, ElIcon } from 'element-plus'

// 路由实例和当前路由信息
const router = useRouter()
const route = useRoute()

// 响应式数据
const movieDetail = ref({}) // 电影详情
const isLogin = ref(false) // 是否登录
const userId = ref('') // 用户ID
const hasRated = ref(false) // 是否已评分
const showRatingDialog = ref(false) // 评分弹窗显示状态

// 评分表单数据
const ratingForm = reactive({
  score: 0, // 评分（1.0-5.0）
  description: '' // 评论（可选）
})

// 评分表单验证规则
const ratingRules = reactive({
  score: [
    { required: true, message: '请选择评分', trigger: 'change' }
  ]
})

// 表单引用
const ratingFormRef = ref(null)

// 页面加载时执行
onMounted(() => {
  // 获取当前电影ID（从路由参数中获取）
  const movieId = route.params.id
  if (movieId) {
    getMovieDetail(movieId)
  }
  
  // 检查登录状态
  const storedUserId = localStorage.getItem('userId')
  if (storedUserId) {
    isLogin.value = true
    userId.value = storedUserId
    // 检查是否已评分
    checkHasRated(storedUserId, movieId)
  }
})

// 监听路由变化（如果从其他电影详情页跳转过来）
watch(route, (newRoute) => {
  const movieId = newRoute.params.id
  getMovieDetail(movieId)
  if (isLogin.value) {
    checkHasRated(userId.value, movieId)
  }
})

// 获取电影详情（调用后端接口）
const getMovieDetail = async (movieId) => {
  try {
    const response = await axios.get(`http://localhost:5000/api/movie/detail/${movieId}`)
    console.log('电影详情接口返回：', response.data) // 🔥 新增调试日志，查看picture字段
    if (response.data.code === 1) {
      movieDetail.value = response.data.data
    } else {
      ElMessage.warning(response.data.msg)
      movieDetail.value = {}
    }
  } catch (error) {
    ElMessage.error('获取电影详情失败，请稍后再试')
    console.error('Error:', error)
    movieDetail.value = {}
  }
}

// 检查是否已评分（调用后端接口）
const checkHasRated = async (userId, movieId) => {
  try {
    // 后端暂无单独的"检查评分"接口，通过查询评分表实现（实际项目可优化为单独接口）
    const response = await axios.get('http://localhost:5000/api/user/rating/check', {
      params: {
        uid: userId,
        mid: movieId
      }
    })
    // 注：此处为简化处理，实际需后端配合返回是否已评分；当前先用"是否有评分记录"判断
    // （因后端user_rating表有unique约束，重复评分会报错，也可通过add_rating接口的报错判断）
    hasRated.value = false // 暂设为false，实际项目需根据后端返回修改
  } catch (error) {
    console.error('检查评分状态失败:', error)
  }
}

// 处理评分提交
const handleRating = async () => {
  if (!ratingFormRef.value) return
  try {
    await ratingFormRef.value.validate()
    
    // 调用后端评分接口
    const response = await axios.post('http://localhost:5000/api/user/rating/add', {
      uid: parseInt(userId.value),
      mid: parseInt(route.params.id),
      score: ratingForm.score,
      description: ratingForm.description
    })
    
    if (response.data.code === 1) {
      ElMessage.success('评分成功！')
      showRatingDialog.value = false
      hasRated.value = true
      // 刷新电影详情（更新评分）
      getMovieDetail(route.params.id)
      
      // 重置评分表单
      ratingForm.score = 0
      ratingForm.description = ''
    } else {
      ElMessage.error(response.data.msg)
      if (response.data.msg.includes('已对该电影评分')) {
        hasRated.value = true
        showRatingDialog.value = false
      }
    }
  } catch (error) {
    if (error.name === 'ValidationError') {
      ElMessage.warning('请选择评分')
    } else {
      ElMessage.error('评分失败，请稍后再试')
      console.error('Rating error:', error)
    }
  }
}

// 关闭评分弹窗时重置表单
const handleDialogClose = () => {
  ratingForm.score = 0
  ratingForm.description = ''
  if (ratingFormRef.value) {
    ratingFormRef.value.clearValidate()
  }
}

// 返回上一页
const goBack = () => {
  router.go(-1)
}
</script>

<style scoped>
.el-rate {
  font-size: 24px;
}

.dialog-footer {
  text-align: right;
}

/* 🔥 新增：修复图片预览层级 */
:deep(.el-image-viewer__wrapper) {
  z-index: 9999 !important;
}
</style>