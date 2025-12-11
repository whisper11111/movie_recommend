<template>
  <div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
      <h2>电影管理</h2>
      <el-button type="primary" @click="showAddDialog = true">添加电影</el-button>
    </div>

    <!-- 电影列表 -->
    <el-table :data="movieList" border style="width: 100%;" v-loading="loading">
      <el-table-column prop="id" label="电影ID" width="80"></el-table-column>
      <el-table-column prop="name" label="电影名称" min-width="150"></el-table-column>
      <el-table-column prop="director" label="导演" min-width="120"></el-table-column>
      <el-table-column prop="style" label="类型" min-width="100"></el-table-column>
      <el-table-column prop="release_date" label="上映日期" width="120">
        <template #default="scope">
          {{ scope.row.release_date || '未设置' }}
        </template>
      </el-table-column>
      <!-- 海报预览（从二进制转Base64） -->
      <el-table-column label="海报预览" width="100">
        <template #default="scope">
          <el-image 
            v-if="scope.row.picture" 
            :src="`data:image/jpeg;base64,${scope.row.picture}`" 
            style="width: 80px; height: 100px;" 
            fit="cover"
            preview-src-list="['data:image/jpeg;base64,' + scope.row.picture]"
          ></el-image>
          <span v-else>无海报</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-button size="small" @click="editMovie(scope.row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 添加/编辑电影弹窗 -->
    <el-dialog :title="isEdit ? '编辑电影' : '添加电影'" v-model="showAddDialog" width="800px">
      <el-form :model="movieForm" label-width="100px" ref="movieFormRef" :rules="formRules">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电影名称" prop="name">
              <el-input v-model="movieForm.name" placeholder="请输入电影名称"></el-input>
            </el-form-item>
            <el-form-item label="导演" prop="director">
              <el-input v-model="movieForm.director" placeholder="请输入导演姓名"></el-input>
            </el-form-item>
            <el-form-item label="演员" prop="actors">
              <el-input v-model="movieForm.actors" placeholder="例如：张三,李四"></el-input>
            </el-form-item>
            <el-form-item label="语言" prop="language">
              <el-input v-model="movieForm.language" placeholder="例如：普通话/英语"></el-input>
            </el-form-item>
            <el-form-item label="出品公司" prop="company">
              <el-input v-model="movieForm.company" placeholder="请输入出品公司"></el-input>
            </el-form-item>
            <el-form-item label="电影类型" prop="style">
              <el-input v-model="movieForm.style" placeholder="例如：科幻/冒险/喜剧"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="上映日期" prop="release_date">
              <el-date-picker 
                v-model="movieForm.release_date" 
                type="date" 
                placeholder="选择上映日期" 
                style="width: 100%;"
                value-format="YYYY-MM-DD"
              ></el-date-picker>
            </el-form-item>
            <el-form-item label="时长" prop="duration">
              <el-input v-model="movieForm.duration" placeholder="例如：120分钟"></el-input>
            </el-form-item>
            <el-form-item label="电影简介" prop="description">
              <el-input 
                v-model="movieForm.description" 
                type="textarea" 
                :rows="6" 
                placeholder="请输入电影简介..."
              ></el-input>
            </el-form-item>
            <!-- 海报上传（转Base64存储到picture字段） -->
            <el-form-item label="电影海报">
              <el-upload
                class="avatar-uploader"
                :show-file-list="false"
                :on-change="handlePosterChange"
                :before-upload="beforeUpload"
                accept="image/jpeg,image/png"
              >
                <!-- 海报预览图（兼容编辑时的Base64） -->
                <img 
                  v-if="movieForm.posterPreview" 
                  :src="movieForm.posterPreview" 
                  style="width: 150px; height: 200px; object-fit: cover; cursor: pointer;"
                >
                <!-- +号上传按钮（无海报时显示） -->
                <div v-else style="width: 150px; height: 200px; border: 1px dashed #d9d9d9; border-radius: 6px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
                  <i class="el-icon-plus" style="font-size: 24px; color: #8c939d;"></i>
                </div>
              </el-upload>
              <div style="color: #999; font-size: 12px; margin-top: 8px;">
                提示：仅支持jpg/png格式，大小不超过2MB
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="resetForm">取消</el-button>
        <el-button type="primary" @click="saveMovie">{{ isEdit ? '更新' : '添加' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 后端基础地址（匹配后端5000端口）
const baseUrl = 'http://localhost:5000'
// 核心修复：拆分接口前缀（列表用公共路径，新增/编辑用管理员路径）
const publicApiPrefix = '/api/movie'       // 公共接口（列表/详情）- 所有人可访问
const adminApiPrefix = '/api/admin/movie'  // 管理员接口（新增/编辑）- 仅管理员可访问

// 数据定义
const movieList = ref([])
const showAddDialog = ref(false)
const isEdit = ref(false)
const loading = ref(false)
const movieFormRef = ref(null)

// 表单验证规则
const formRules = ref({
  name: [{ required: true, message: '请输入电影名称', trigger: 'blur' }],
  director: [{ required: true, message: '请输入导演姓名', trigger: 'blur' }],
  style: [{ required: true, message: '请输入电影类型', trigger: 'blur' }]
})

// 表单字段（完全匹配数据库）
const movieForm = ref({ 
  id: '',
  name: '', 
  director: '', 
  actors: '',
  language: '',
  company: '',
  style: '',
  release_date: '',
  duration: '',
  description: '',
  picture: '', // 海报Base64字符串（不再是二进制）
  posterPreview: '' // 海报预览URL
})  

// 获取电影列表（改用公共接口前缀，保证能显示）
const getMovies = async () => {
  try {
    loading.value = true
    // 清空列表防止旧数据干扰
    movieList.value = []
    // 核心修复：请求公共列表接口 /api/movie/list
    const res = await axios.get(`${baseUrl}${publicApiPrefix}/list`, { 
      params: { page: 1, page_size: 100 },
      timeout: 10000 // 超时时间10秒
    })
    console.log('获取电影列表响应：', res.data)
    if (res.data.code === 1) {
      movieList.value = res.data.data.movie_list || []
      ElMessage.success(`成功加载 ${movieList.value.length} 部电影`)
    } else {
      ElMessage.error('获取电影列表失败：' + (res.data.msg || '未知错误'))
    }
  } catch (e) {
    console.error('获取电影列表报错：', e)
    ElMessage.error(
      e.response 
        ? `接口请求失败：${e.response.status} - ${e.response.data?.msg || '服务器错误'}`
        : e.message.includes('timeout') 
          ? '请求超时：请检查后端服务是否启动'
          : '接口请求失败：请检查后端服务是否启动'
    )
  } finally {
    loading.value = false
  }
}

// 编辑电影（回显数据）
const editMovie = (row) => {
  try {
    isEdit.value = true
    console.log('编辑电影数据：', row)
    // 回显所有字段（海报预览兼容空值）
    movieForm.value = {
      id: row.id || '',
      name: row.name || '',
      director: row.director || '',
      actors: row.actors || '',
      language: row.language || '',
      company: row.company || '',
      style: row.style || '',
      release_date: row.release_date || '',
      duration: row.duration || '',
      description: row.description || '',
      picture: row.picture || '',
      // 体验优化：编辑时海报预览直接用Base64拼接，避免空值
      posterPreview: row.picture ? `data:image/jpeg;base64,${row.picture}` : ''
    }
    showAddDialog.value = true
  } catch (e) {
    console.error('回显电影数据报错：', e)
    ElMessage.error('加载电影数据失败：' + e.message)
  }
}

// 重置表单
const resetForm = () => {
  try {
    showAddDialog.value = false
    // 重置表单验证状态
    if (movieFormRef.value) {
      movieFormRef.value.resetFields()
    }
    // 清空表单数据（强制清空ID）
    movieForm.value = { 
      id: '', 
      name: '', 
      director: '', 
      actors: '',
      language: '',
      company: '',
      style: '',
      release_date: '',
      duration: '',
      description: '',
      picture: '', 
      posterPreview: ''
    }
    isEdit.value = false
  } catch (e) {
    console.error('重置表单报错：', e)
  }
}

// 海报上传前校验
const beforeUpload = (file) => {
  const isImage = file.type === 'image/jpeg' || file.type === 'image/png'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('仅支持上传JPG/PNG格式的图片！')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过2MB！')
    return false
  }
  return true
}

// 海报上传后转Base64（直接存在picture字段）
const handlePosterChange = (file) => {
  try {
    if (!file.raw) {
      ElMessage.warning('请选择有效的图片文件')
      return
    }
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        // 截取Base64前缀后的内容（后端直接存储字符串）
        const base64Str = e.target.result.split(',')[1]
        if (!base64Str) {
          ElMessage.error('图片编码失败：无效的Base64格式')
          return
        }
        movieForm.value.picture = base64Str
        movieForm.value.posterPreview = e.target.result // 预览用
        ElMessage.success('海报预览加载成功')
      } catch (e) {
        console.error('Base64处理报错：', e)
        ElMessage.error('海报处理失败：' + e.message)
      }
    }
    reader.onerror = (e) => {
      console.error('文件读取错误：', e)
      ElMessage.error('图片读取失败：请重新选择文件')
    }
    reader.readAsDataURL(file.raw)
  } catch (e) {
    console.error('海报上传处理报错：', e)
    ElMessage.error('海报上传失败：' + e.message)
  }
}

// 保存电影（添加/编辑）- 改用管理员接口前缀
const saveMovie = async () => {
  try {
    // 表单验证
    if (!movieFormRef.value) return
    const validateResult = await movieFormRef.value.validate()
    if (!validateResult) {
      return
    }

    const adminId = localStorage.getItem('userId')
    if (!adminId) {
      ElMessage.warning('请先登录管理员账号！')
      // 提示跳转到登录页
      ElMessageBox.confirm(
        '未检测到管理员登录状态',
        '登录提示',
        {
          confirmButtonText: '去登录',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        // 这里可以跳转到登录页，示例：window.location.href = '/login'
        ElMessage.info('请先完成管理员登录')
      })
      return
    }

    // 规范请求头（适配后端管理员权限校验）
    const headers = { 
      Authorization: adminId, // 简化格式，直接传userId（适配多数后端校验逻辑）
      'Content-Type': 'application/json;charset=UTF-8'
    }
    
    // 关键优化：空值处理改为空字符串（避免后端None调用strip报错）
    const formData = {
      name: movieForm.value.name.trim(),
      director: movieForm.value.director.trim(),
      actors: movieForm.value.actors.trim() || '',
      language: movieForm.value.language.trim() || '',
      company: movieForm.value.company.trim() || '',
      style: movieForm.value.style.trim(),
      release_date: movieForm.value.release_date ? movieForm.value.release_date.trim() : '',
      duration: movieForm.value.duration.trim() || '',
      description: movieForm.value.description.trim() || '',
      picture: movieForm.value.picture || ''
    }

    console.log(`提交${isEdit.value ? '编辑' : '新建'}数据：`, formData)
    let res
    if (isEdit.value) {
      // 编辑电影（带ID）- 管理员接口
      if (!movieForm.value.id) {
        ElMessage.error('电影ID不能为空！')
        return
      }
      res = await axios.put(
        `${baseUrl}${adminApiPrefix}/update/${movieForm.value.id}`,
        formData,
        { headers, timeout: 10000 }
      )
    } else {
      // 添加电影（强制清空ID）- 管理员接口
      movieForm.value.id = ''
      res = await axios.post(
        `${baseUrl}${adminApiPrefix}/add`,
        formData,
        { headers, timeout: 10000 }
      )
    }

    console.log('保存电影响应：', res.data)
    if (res.data.code === 1) {
      ElMessage.success(isEdit.value ? '电影更新成功' : '电影添加成功')
      resetForm()
      // 重新加载列表
      await getMovies()
    } else {
      ElMessage.error((isEdit.value ? '更新' : '添加') + '失败：' + (res.data.msg || '未知错误'))
    }
  } catch (e) {
    // 增强错误日志，方便定位问题
    console.error('保存电影报错详情：', {
      url: e.config?.url,
      method: e.config?.method,
      requestData: e.config?.data,
      status: e.response?.status,
      responseData: e.response?.data,
      message: e.message
    })
    // 友好的错误提示
    let errorMsg = '操作失败：'
    if (e.response) {
      errorMsg += `${e.response.status} - ${e.response.data?.msg || '服务器处理失败'}`
      if (e.response.status === 401) {
        errorMsg += '（管理员权限不足或未登录）'
      } else if (e.response.status === 404) {
        errorMsg += '（接口地址不存在，请检查后端接口路径）'
      } else if (e.response.status === 500) {
        errorMsg += '（服务器内部错误，请查看后端日志）'
      }
    } else if (e.message.includes('timeout')) {
      errorMsg += '请求超时（后端服务未启动或网络问题）'
    } else if (e.message.includes('Network Error')) {
      errorMsg += '网络错误（请检查后端服务是否启动）'
    } else {
      errorMsg += e.message
    }
    ElMessage.error(errorMsg)
  }
}

// 页面加载时获取电影列表
onMounted(() => {
  console.log('电影管理页面加载完成，开始获取电影列表')
  getMovies()
})
</script>

<style scoped>
/* 修复上传按钮样式 */
.avatar-uploader {
  display: inline-block;
  width: 150px;
  height: 200px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

/* 确保上传按钮可点击 */
.avatar-uploader:hover {
  border-color: #409eff;
}

/* 预览图样式 */
.avatar-uploader img {
  border-radius: 6px;
}

/* 上传提示文字 */
.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}
</style>