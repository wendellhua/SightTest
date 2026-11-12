<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()

const email = ref('')
const password = ref('')
const loading = ref(false)

async function onSubmit() {
  if (!email.value || !password.value) {
    ElMessage.warning('请输入邮箱和密码')
    return
  }
  loading.value = true
  try {
    await userStore.doLogin(email.value, password.value)
    if (userStore.user?.status === 'cancelling') {
      ElMessage.warning('账号处于注销冷静期，可前往设置撤销注销')
    } else {
      ElMessage.success('登录成功')
    }
    router.push('/home')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login">
    <el-card class="login-card">
      <div class="login-title">SightTest</div>
      <div class="login-subtitle">Web 端智能测试系统</div>
      <el-input v-model="email" placeholder="邮箱" class="login-field" />
      <el-input
        v-model="password"
        type="password"
        placeholder="密码"
        show-password
        class="login-field"
        @keyup.enter="onSubmit"
      />
      <el-button type="primary" class="login-btn" :loading="loading" @click="onSubmit">登录</el-button>
      <div class="login-links">
        <router-link to="/register">注册账号</router-link>
        <span class="sep">·</span>
        <a @click="$message.info('找回密码待实现')">忘记密码</a>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.login {
  height: 100%;
  display: grid;
  place-items: center;
}
.login-card {
  width: 380px;
}
.login-title {
  text-align: center;
  font-size: 26px;
  font-weight: 700;
  color: var(--st-primary);
}
.login-subtitle {
  text-align: center;
  color: var(--st-text-2);
  margin: 8px 0 24px;
}
.login-field {
  margin-bottom: 16px;
}
.login-btn {
  width: 100%;
}
.login-links {
  margin-top: 16px;
  text-align: center;
  font-size: 13px;
  color: var(--st-text-2);
}
.login-links a {
  color: var(--st-primary);
  cursor: pointer;
}
.sep {
  margin: 0 8px;
}
</style>
