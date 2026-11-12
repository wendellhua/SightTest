<script setup lang="ts">
import { createModel, deleteModel, listModels, testModel, updateModel, type ModelConfig } from '@/api/model'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'

const models = ref<ModelConfig[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const form = reactive({ name: '', base_url: '', api_key: '', model: '' })
const saving = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await listModels()
    models.value = res.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.name = ''
  form.base_url = ''
  form.api_key = ''
  form.model = ''
  dialogVisible.value = true
}

function openEdit(m: ModelConfig) {
  editingId.value = m.id
  form.name = m.name
  form.base_url = m.base_url
  form.api_key = ''
  form.model = m.model
  dialogVisible.value = true
}

async function onSave() {
  if (!form.name || !form.base_url || !form.model) {
    ElMessage.warning('请填写名称、Base URL 与模型名称')
    return
  }
  if (!editingId.value && !form.api_key) {
    ElMessage.warning('请填写 API Key')
    return
  }
  saving.value = true
  try {
    const payload: { name: string; base_url: string; model: string; api_key?: string } = {
      name: form.name,
      base_url: form.base_url,
      model: form.model,
    }
    if (form.api_key) payload.api_key = form.api_key

    if (editingId.value) {
      await updateModel(editingId.value, payload)
    } else {
      await createModel({ name: form.name, base_url: form.base_url, api_key: form.api_key!, model: form.model })
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function onTest(m: ModelConfig) {
  const res = await testModel(m.id)
  if (res.data.ok) {
    ElMessage.success(res.data.message)
  } else {
    ElMessage.error(res.data.message)
  }
}

async function onDelete(m: ModelConfig) {
  await ElMessageBox.confirm(`确定删除模型配置「${m.name}」？`, '删除确认', { type: 'warning' })
  await deleteModel(m.id)
  ElMessage.success('已删除')
  await load()
}

onMounted(load)
</script>

<template>
  <div class="model">
    <div class="toolbar">
      <h2>模型配置</h2>
      <el-button type="primary" @click="openCreate">新增配置</el-button>
    </div>

    <el-table v-loading="loading" :data="models" border>
      <el-table-column prop="name" label="名称" min-width="120" />
      <el-table-column prop="model" label="模型" min-width="120" />
      <el-table-column prop="base_url" label="Base URL" min-width="220" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'verified' ? 'success' : 'info'" size="small">
            {{ row.status === 'verified' ? '已通过' : '未检测' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button size="small" @click="onTest(row)">检测</el-button>
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" plain @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑模型配置' : '新增模型配置'" width="520px">
      <el-form label-position="top">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="例如：GPT-4o" maxlength="100" />
        </el-form-item>
        <el-form-item label="Base URL" required>
          <el-input v-model="form.base_url" placeholder="https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item label="模型名称" required>
          <el-input v-model="form.model" placeholder="例如：gpt-4o" maxlength="100" />
        </el-form-item>
        <el-form-item :label="editingId ? 'API Key（留空则不修改）' : 'API Key'" :required="!editingId">
          <el-input v-model="form.api_key" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">保存并检测</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.toolbar h2 {
  margin: 0;
  font-size: 20px;
}
</style>
