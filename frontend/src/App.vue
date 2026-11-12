<script setup lang="ts">
import { Connection, HomeFilled, Management, Setting, TrendCharts } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isAuthPage = computed(() => route.meta.public === true)

onMounted(() => {
  void userStore.fetchUser()
})

function logout() {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<template>
  <router-view v-if="isAuthPage" />

  <el-container v-else class="app-shell">
    <el-aside width="240px" class="app-aside">
      <div class="app-logo">SightTest</div>
      <el-menu :default-active="route.path" router class="app-menu">
        <el-menu-item index="/projects">
          <el-icon><HomeFilled /></el-icon>
          <span>平台首页</span>
        </el-menu-item>
        <el-menu-item index="/models">
          <el-icon><Connection /></el-icon>
          <span>模型配置</span>
        </el-menu-item>
        <el-menu-item index="/usage">
          <el-icon><TrendCharts /></el-icon>
          <span>用量与成本</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>设置</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.user?.is_admin" index="/admin">
          <el-icon><Management /></el-icon>
          <span>后台管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <span>Web 端智能测试系统</span>
        <div class="header-right">
          <span class="user-name">{{ userStore.user?.name ?? userStore.user?.email ?? '' }}</span>
          <el-button link @click="logout">退出登录</el-button>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-shell {
  height: 100%;
}
.app-aside {
  background: #ffffff;
  border-right: 1px solid var(--st-border);
}
.app-logo {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  font-size: 20px;
  font-weight: 700;
  color: var(--st-primary);
  letter-spacing: 0.5px;
}
.app-menu {
  border-right: none;
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border-bottom: 1px solid var(--st-border);
  font-size: 15px;
  color: var(--st-text-2);
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-name {
  color: var(--st-text);
}
.app-main {
  padding: 24px;
}
</style>
