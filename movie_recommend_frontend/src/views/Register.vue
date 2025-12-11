<template>
  <div style="display: flex; justify-content: center; align-items: center; min-height: 60vh;">
    <el-card shadow="hover" style="width: 400px;">
      <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #409eff;">用户注册</h2>
      </div>
      
      <!-- 注册表单 -->
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="80px">


        <el-form-item label="用户名" prop="name">
          <el-input v-model="registerForm.name" placeholder="请输入用户名">
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="请输入您的邮箱">
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码（6-20位）">
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请再次输入密码">
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>













        <el-form-item label="性别" prop="sex">
          <el-radio-group v-model="registerForm.sex">
            <el-radio label="1">男</el-radio>
            <el-radio label="0">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item style="text-align: center;">
          <el-button type="primary" @click="handleRegister" style="width: 100%;">注册</el-button>
        </el-form-item>
        <el-form-item style="text-align: center;">
          <span>已有账号？</span>
          <el-link @click="goToLogin">立即登录</el-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElForm, ElFormItem, ElInput, ElButton, ElLink, ElRadioGroup, ElRadio } from 'element-plus'

// 路由实例
const router = useRouter()

// 表单引用（用于表单验证）
const registerFormRef = ref(null)

// 注册表单数据
const registerForm = reactive({
  name: '', // 用户名
  email: '', // 邮箱
  password: '', // 密码
  confirmPassword: '', // 确认密码
  sex: '' // 性别（1=男，0=女）
})

// 注册表单验证规则
const registerRules = reactive({
  name: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 10, message: '用户名长度在2-10个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6-20个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  sex: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ]
})

// 处理注册逻辑
const handleRegister = async () => {
  // 先验证表单
  if (!registerFormRef.value) return
  try {
    await registerFormRef.value.validate()
    
    // 调用后端注册接口（注意：性别需要转为数字）
    const response = await axios.post('http://localhost:5000/api/user/register', {
      name: registerForm.name,
      email: registerForm.email,
      password: registerForm.password,
      sex: parseInt(registerForm.sex) // 转为数字（1/0）
    })
    
    // 处理注册结果
    if (response.data.code === 1) {
      ElMessage.success(response.data.msg)
      // 注册成功后跳转到登录页
      router.push('/login')
    } else {
      ElMessage.error(response.data.msg)
    }
  } catch (error) {
    // 表单验证失败或接口调用失败
    if (error.name === 'ValidationError') {
      ElMessage.warning('请填写正确的表单信息')
    } else {
      ElMessage.error('注册失败，请稍后再试')
      console.error('Register error:', error)
    }
  }
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.el-form-item {
  margin-bottom: 15px;
}
.el-radio-group {
  display: flex;
  gap: 20px;
}
</style>