<script setup lang="ts">
import type { ModelConfig } from '@/api/model'
import { listModels } from '@/api/model'
import { checkUrl, createProject, type AccountInput } from '@/api/project'
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const name = ref('')
const url = ref('')
const modelId = ref<number | null>(null)
const models = ref<ModelConfig[]>([])
const accounts = ref<AccountInput[]>([{ username: '', password: '', is_primary: true }])
const checking = ref(false)
const urlStatus = ref<'idle' | 'ok' | 'fail'>('idle')
const submitting = ref(false)

async function loadModels() {
  const res = await listModels()
  models.value = res.data
}

async function onCheckUrl() {
  if (!url.value) {
    ElMessage.warning('请输入 URL')
    return
  }
  checking.value = true
  urlStatus.value = 'idle'
  try {
    const res = await checkUrl(url.value)
    urlStatus.value = res.data.reachable ? 'ok' : 'fail'
  } finally {
    checking.value = false
  }
}

function addAccount() {
  accounts.value.push({ username: '', password: '', is_primary: false })
}

function removeAccount(index: number) {
  accounts.value.splice(index, 1)
}

async function onSubmit() {
  if (!name.value || !url.value) {
    ElMessage.warning('请填写项目名称和 URL')
    return
  }
  if (accounts.value.length === 0) {
    ElMessage.warning('请至少添加一组测试账号')
    return
  }
  if (accounts.value.some((a) => !a.username || !a.password)) {
    ElMessage.warning('请填写完整的测试账号信息')
    return
  }
  submitting.value = true
  try {
    await createProject({
      name: name.value,
      url: url.value,
      model_config_id: modelId.value,
      accounts: accounts.value,
    })
    ElMessage.success('项目创建成功')
    router.push('/projects')
  } finally {
    submitting.value = false
  }
}

onMounted(loadModels)
</script>

<template>
  <div class="create">
    <el-card class="card">
      <template #header>
        <span class="title">创建项目</span>
      </template>

      <el-form label-position="top">
        <el-form-item label="项目名称" required>
          <el-input v-model="name" placeholder="例如：某电商网站" maxlength="100" />
        </el-form-item>

        <el-form-item label="被测网站 URL" required>
          <div class="url-row">
            <el-input v-model="url" placeholder="https://example.com" />
            <el-button :loading="checking" @click="onCheckUrl">检测</el-button>
          </div>
          <div v-if="urlStatus === 'ok'" class="url-tip ok">URL 可访问</div>
          <div v-else-if="urlStatus === 'fail'" class="url-tip fail">URL 不可访问</div>
        </el-form-item>

        <el-form-item label="绑定模型（可选）">
          <el-select v-model="modelId" placeholder="选择模型配置" clearable style="width: 100%">
            <el-option v-for="m in models" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="测试账号（至少 1 组）">
          <div v-for="(acc, index) in accounts" :key="index" class="account-row">
            <el-input v-model="acc.username" placeholder="用户名" class="account-field" />
            <el-input v-model="acc.password" type="password" placeholder="密码" show-password class="account-field" />
            <el-checkbox v-model="acc.is_primary">主账号</el-checkbox>
            <el-button v-if="accounts.length > 1" type="danger" text @click="removeAccount(index)">删除</el-button>
          </div>
          <el-button text type="primary" @click="addAccount">+ 添加账号</el-button>
        </el-form-item>

        <el-button type="primary" :loading="submitting" @click="onSubmit">创建</el-button>
        <el-button @click="router.push('/projects')">取消</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.create {
  max-width: 720px;
  margin: 0 auto;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
.url-row {
  display: flex;
  gap: 12px;
  width: 100%;
}
.url-tip {
  font-size: 12px;
  margin-top: 4px;
}
.url-tip.ok {
  color: #16a34a;
}
.url-tip.fail {
  color: #dc2626;
}
.account-row {
  display: flex;
  gap: 12px;
  align-items: center;
  width: 100%;
  margin-bottom: 8px;
}
.account-field {
  width: 180px;
}
</style>
