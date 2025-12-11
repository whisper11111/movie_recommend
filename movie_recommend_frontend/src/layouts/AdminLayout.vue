<template>
  <el-container style="min-height: 100vh;">
    <el-aside width="200px" style="background-color: #304156; color: white;">
      <el-menu 
        default-active="1" 
        class="el-menu-vertical-demo" 
        background-color="#304156" 
        text-color="white" 
        active-text-color="#ffd04b"
      >
        <el-menu-item index="1" route="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="2" route="/admin/movies">
          <el-icon><Video /></el-icon>
          <span>电影管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>

</script>