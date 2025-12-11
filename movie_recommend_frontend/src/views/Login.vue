<template>
  <div style="display: flex; justify-content: center; align-items: center; min-height: 60vh;">
    <el-card shadow="hover" style="width: 400px;">
      <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #409eff;">用户登录</h2>
      </div>
      
      <!-- 登录表单 -->
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="80px">

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="loginForm.email" placeholder="请输入您的邮箱">
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入您的密码">
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>


        <el-form-item style="text-align: center;">
          <el-button type="primary" @click="handleLogin" style="width: 100%;">登录</el-button>
        </el-form-item>
        <el-form-item style="text-align: center;">
          <span>还没有账号？</span>
          <el-link @click="goToRegister">立即注册</el-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElForm, ElFormItem, ElInput, ElButton, ElLink } from 'element-plus'

// 路由实例
const router = useRouter()

// 表单引用（用于表单验证）
const loginFormRef = ref(null)

// 登录表单数据
const loginForm = reactive({
  email: '', // 邮箱
  password: '' // 密码
})

// 登录表单验证规则
const loginRules = reactive({
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6-20个字符之间', trigger: 'blur' }
  ]
})

// 处理登录逻辑
const handleLogin = async () => {
  // 先验证表单
  if (!loginFormRef.value) return
  try {
    await loginFormRef.value.validate()
    
    // 调用后端登录接口
    const response = await axios.post('http://localhost:5000/api/user/login', {
      email: loginForm.email,
      password: loginForm.password
    })
    
    // 处理登录结果
    if (response.data.code === 1) {
      // 登录成功：存储用户信息到本地存储（刷新页面后保持登录）
      localStorage.setItem('userId', response.data.data.user_id)
      localStorage.setItem('username', response.data.data.username)
      
      // 显示成功消息
      ElMessage.success(response.data.msg)
      
      // 跳转到首页
      router.push('/')
    } else {
      // 登录失败：显示错误消息
      ElMessage.error(response.data.msg)
    }
  } catch (error) {
    // 表单验证失败或接口调用失败
    if (error.name === 'ValidationError') {
      ElMessage.warning('请填写正确的表单信息')
    } else {
      ElMessage.error('登录失败，请稍后再试')
      console.error('Login error:', error)
    }
  }
}

// 跳转到注册页
const goToRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
/* 调整表单间距 */
.el-form-item {
  margin-bottom: 20px;
}
</style>