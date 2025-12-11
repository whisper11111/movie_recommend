<template>
  <div>
    <h2>用户管理</h2>
    <el-table :data="userList" border style="width: 100%; margin-top: 20px;" v-loading="loading">
      <el-table-column prop="id" label="用户ID" width="80"></el-table-column>
      <el-table-column prop="name" label="用户名" min-width="120"></el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="200"></el-table-column>
      <el-table-column prop="sex" label="性别" width="80">
        <template #default="scope">
          {{ scope.row.sex || '未填写' }}
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="注册时间" min-width="180">
        <template #default="scope">
          {{ scope.row.create_time ? new Date(scope.row.create_time).toLocaleString() : '未知' }}
        </template>
      </el-table-column>
      <el-table-column prop="is_admin" label="身份" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_admin ? 'danger' : 'primary'">
            {{ scope.row.is_admin ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" type="primary" @click="viewBehavior(scope.row.id)">
            查看行为记录
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 行为记录弹窗 -->
    <el-dialog 
      title="用户行为记录" 
      v-model="behaviorDialogVisible" 
      width="800px"
      append-to-body
    >
      <el-table :data="behaviorList" border v-loading="behaviorLoading">
        <el-table-column prop="type" label="行为类型" width="120"></el-table-column>
        <el-table-column prop="movie_name" label="电影名称" min-width="200"></el-table-column>
        <el-table-column prop="score" label="评分" width="80">
          <template #default="scope">
            {{ scope.row.type === '评分' ? (scope.row.score || '无') : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="time" label="时间" min-width="180">
          <template #default="scope">
            {{ scope.row.time ? new Date(scope.row.time).toLocaleString() : '未知' }}
          </template>
        </el-table-column>
      </el-table>
      <div v-if="behaviorList.length === 0 && !behaviorLoading" style="text-align: center; padding: 20px;">
        该用户暂无行为记录
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 核心：配置后端基础地址
const baseUrl = 'http://localhost:5000'

// 数据定义
const userList = ref([])
const behaviorDialogVisible = ref(false)
const behaviorList = ref([])
// 加载状态
const loading = ref(false)
const behaviorLoading = ref(false)

// 获取所有用户（修复接口地址 + 完善错误处理 + 加载状态）
const getUsers = async () => {
  try {
    loading.value = true
    const userId = localStorage.getItem('userId')
    
    // 校验管理员是否登录
    if (!userId) {
      ElMessage.warning('请先登录管理员账号！')
      loading.value = false
      return
    }

    // 修复：使用完整后端接口地址
    const res = await axios.get(`${baseUrl}/api/admin/users`, {
      headers: { Authorization: userId }
    })
    
    if (res.data.code === 1) {
      userList.value = res.data.data || []
    } else {
      ElMessage.error('获取用户列表失败：' + res.data.msg)
    }
  } catch (e) {
    console.error('获取用户列表报错：', e)
    ElMessage.error('获取用户列表失败：' + (e.response?.data?.msg || '接口请求异常'))
  } finally {
    loading.value = false
  }
}

// 查看用户行为记录（修复接口地址 + 完善体验）
const viewBehavior = async (userId) => {
  try {
    behaviorLoading.value = true
    const adminId = localStorage.getItem('userId')
    
    if (!adminId) {
      ElMessage.warning('请先登录管理员账号！')
      behaviorLoading.value = false
      return
    }

    // 修复：使用完整后端接口地址
    const res = await axios.get(`${baseUrl}/api/admin/user/behavior/${userId}`, {
      headers: { Authorization: adminId }
    })
    
    if (res.data.code === 1) {
      behaviorList.value = res.data.data || []
    } else {
      ElMessage.error('获取行为记录失败：' + res.data.msg)
      behaviorList.value = []
    }
    
    behaviorDialogVisible.value = true
  } catch (e) {
    console.error('获取行为记录报错：', e)
    ElMessage.error('获取行为记录失败：' + (e.response?.data?.msg || '接口请求异常'))
    behaviorList.value = []
    behaviorDialogVisible.value = true
  } finally {
    behaviorLoading.value = false
  }
}

// 页面加载时获取用户列表
onMounted(() => getUsers())
</script>

<style scoped>
.el-tag {
  font-size: 12px;
}
.el-button--small {
  padding: 5px 10px;
}
</style>