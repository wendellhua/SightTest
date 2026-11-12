<script setup lang="ts">
import { getSetting, updateSetting } from '@/api/setting'
import { requestCancel, revokeCancel } from '@/api/user'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'

const userStore = useUserStore()
const saving = ref(false)
const form = reactive({ explore_minutes: 60, explore_pages: 200, stress_limit: 50, account_stress_limit: 10 })

async function load() {
  const res = await getSetting()
  Object.assign(form, res.data)
}

async function onSave() {
  saving.value = true
  try {
    await updateSetting({ ...form })
    ElMessage.success('保存成功')
  } finally {
    saving.value = false
  }
}

async function onCancelAccount() {
  await ElMessageBox.confirm('申请注销后进入 7 天冷静期，期间账号冻结。确定继续？', '账号注销', {
    type: 'warning',
    confirmButtonText: '申请注销',
    cancelButtonText: '取消',
  })
  await requestCancel()
  ElMessage.success('已申请注销，7 天内可撤销')
  await userStore.fetchUser()
}

async function onRevokeCancel() {
  await revokeCancel()
  ElMessage.success('已撤销注销申请')
  await userStore.fetchUser()
}

onMounted(load)
</script>

<template>
  <div class="settings">
    <el-card class="card">
      <template #header><span class="title">测试设置</span></template>
      <el-form label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="探索时长上限（分钟）">
              <el-input-number v-model="form.explore_minutes" :min="1" :max="600" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="探索页面数上限">
              <el-input-number v-model="form.explore_pages" :min="1" :max="10000" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单接口压测并发上限">
              <el-input-number v-model="form.stress_limit" :min="1" :max="1000" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单账号压测并发上限">
              <el-input-number v-model="form.account_stress_limit" :min="1" :max="100" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
      </el-form>
    </el-card>

    <el-card class="card danger-card">
      <template #header><span class="title">账号注销</span></template>
      <template v-if="userStore.user?.status === 'cancelling'">
        <p>您的账号已处于注销冷静期，冷静期满后将删除账号及名下全部数据。</p>
        <el-button type="primary" @click="onRevokeCancel">撤销注销</el-button>
      </template>
      <template v-else>
        <p>注销后不可恢复，将删除账号和名下全部项目数据。</p>
        <el-button type="danger" plain @click="onCancelAccount">申请注销</el-button>
      </template>
    </el-card>
  </div>
</template>

<style scoped>
.settings {
  max-width: 720px;
}
.card {
  margin-bottom: 20px;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
.danger-card p {
  color: var(--st-text-2);
  margin: 0 0 16px;
}
</style>
