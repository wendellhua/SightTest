<script setup lang="ts">
import { register as apiRegister, sendCode } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const userStore = useUserStore()

const email = ref('')
const code = ref('')
const name = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const sending = ref(false)
const countdown = ref(0)

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

async function onSendCode() {
  const target = email.value.trim()
  if (!EMAIL_RE.test(target)) {
    ElMessage.warning('请输入有效的邮箱地址')
    return
  }
  sending.value = true
  try {
    await sendCode(target, 'register')
    ElMessage.success(`验证码已发送至 ${target}，请查收邮件（含垃圾箱）`)
    countdown.value = 60
    const timer = window.setInterval(() => {
      countdown.value -= 1
      if (countdown.value <= 0) window.clearInterval(timer)
    }, 1000)
  } finally {
    sending.value = false
  }
}

async function onSubmit() {
  if (!EMAIL_RE.test(email.value.trim())) {
    ElMessage.warning('请输入有效的邮箱地址')
    return
  }
  if (!/^\d{6}$/.test(code.value.trim())) {
    ElMessage.warning('请输入 6 位数字验证码')
    return
  }
  if (!name.value.trim()) {
    ElMessage.warning('请输入姓名')
    return
  }
  if (password.value.length < 8) {
    ElMessage.warning('密码至少 8 位')
    return
  }
  if (password.value !== confirmPassword.value) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    const res = await apiRegister({
      email: email.value.trim(),
      code: code.value.trim(),
      password: password.value,
      name: name.value.trim(),
    })
    userStore.setAuth(res.data.token, res.data.user)
    ElMessage.success('注册成功')
    router.push('/projects')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register">
    <el-card class="register-card">
      <div class="register-title">注册账号</div>
      <div class="register-subtitle">创建您的 SightTest 账号</div>

      <el-input v-model="email" placeholder="邮箱" class="field" />
      <div class="code-row">
        <el-input v-model="code" placeholder="验证码" class="field code-input" />
        <el-button :disabled="countdown > 0" :loading="sending" @click="onSendCode">
          {{ countdown > 0 ? `${countdown}s 后重发` : '发送验证码' }}
        </el-button>
      </div>
      <el-input v-model="name" placeholder="姓名" class="field" />
      <el-input v-model="password" type="password" placeholder="密码（至少 8 位）" show-password class="field" />
      <el-input
        v-model="confirmPassword"
        type="password"
        placeholder="确认密码"
        show-password
        class="field"
        @keyup.enter="onSubmit"
      />

      <el-button type="primary" class="register-btn" :loading="loading" @click="onSubmit">注册</el-button>
      <div class="register-links">
        已有账号？
        <router-link to="/login">去登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.register {
  height: 100%;
  display: grid;
  place-items: center;
}
.register-card {
  width: 400px;
}
.register-title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
}
.register-subtitle {
  text-align: center;
  color: var(--st-text-2);
  margin: 8px 0 24px;
}
.field {
  margin-bottom: 16px;
}
.code-row {
  display: flex;
  gap: 12px;
}
.code-input {
  flex: 1;
}
.register-btn {
  width: 100%;
}
.register-links {
  margin-top: 16px;
  text-align: center;
  font-size: 13px;
  color: var(--st-text-2);
}
.register-links a {
  color: var(--st-primary);
}
</style>
