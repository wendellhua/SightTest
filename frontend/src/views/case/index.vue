<script setup lang="ts">
import { createCase, debugCase, deleteCase, listCases, updateCase, type CaseInput, type CaseItem } from '@/api/case'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.id)

const cases = ref<CaseItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const caseType = ref<string | undefined>()
const loading = ref(false)

const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const saving = ref(false)

const typeText: Record<string, string> = { func: '功能', api: '接口', perf: '性能', mech: '机制' }

const emptyForm = (): CaseInput => ({
  case_type: 'func',
  module_path: null,
  page: null,
  name: '',
  priority: 'P2',
  precondition: null,
  steps: '',
  expect: '',
  automatable: true,
  remark: null,
})
const form = reactive<CaseInput>(emptyForm())

async function load() {
  loading.value = true
  try {
    const res = await listCases(projectId, { case_type: caseType.value, page: page.value, page_size: pageSize })
    cases.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  Object.assign(form, emptyForm())
  dialogVisible.value = true
}

function openEdit(item: CaseItem) {
  editingId.value = item.id
  Object.assign(form, {
    case_type: item.case_type,
    module_path: item.module_path,
    page: item.page,
    name: item.name,
    priority: item.priority,
    precondition: item.precondition,
    steps: item.steps,
    expect: item.expect,
    automatable: item.automatable,
    remark: item.remark,
  })
  dialogVisible.value = true
}

async function onSave() {
  if (!form.name || !form.steps || !form.expect) {
    ElMessage.warning('请填写名称、步骤与预期结果')
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      await updateCase(projectId, editingId.value, { ...form })
    } else {
      await createCase(projectId, { ...form })
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function onDelete(item: CaseItem) {
  await ElMessageBox.confirm(`确定删除用例「${item.name}」？历史执行记录将保留。`, '删除确认', { type: 'warning' })
  await deleteCase(projectId, item.id)
  ElMessage.success('已删除')
  await load()
}

async function onDebug(item: CaseItem) {
  const res = await debugCase(projectId, item.id)
  ElMessage.success('调试已启动')
  await router.push(`/project/${projectId}/execution/${res.data.execution_id}`)
}

function onTypeChange() {
  page.value = 1
  void load()
}

onMounted(load)
</script>

<template>
  <div class="case-page">
    <div class="toolbar">
      <h2>用例管理</h2>
      <div class="toolbar-right">
        <el-select v-model="caseType" placeholder="全部类型" clearable style="width: 140px" @change="onTypeChange">
          <el-option v-for="(text, key) in typeText" :key="key" :label="text" :value="key" />
        </el-select>
        <el-button type="primary" @click="openCreate">新增用例</el-button>
      </div>
    </div>

    <el-table v-loading="loading" :data="cases" border>
      <el-table-column prop="name" label="名称" min-width="200" show-overflow-tooltip />
      <el-table-column label="类型" width="90">
        <template #default="{ row }">{{ typeText[row.case_type] ?? row.case_type }}</template>
      </el-table-column>
      <el-table-column prop="module_path" label="模块" min-width="140" show-overflow-tooltip />
      <el-table-column prop="priority" label="优先级" width="90" />
      <el-table-column prop="result" label="结果" width="90" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="onDebug(row)">调试</el-button>
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" plain @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="load"
      />
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑用例' : '新增用例'" width="640px">
      <el-form label-position="top">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="名称" required>
              <el-input v-model="form.name" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="类型" required>
              <el-select v-model="form.case_type" style="width: 100%">
                <el-option v-for="(text, key) in typeText" :key="key" :label="text" :value="key" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="优先级">
              <el-select v-model="form.priority" style="width: 100%">
                <el-option v-for="p in ['P0', 'P1', 'P2', 'P3']" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="所属模块">
              <el-input v-model="form.module_path" placeholder="如：商城/订单" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属页面">
              <el-input v-model="form.page" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="前置条件">
          <el-input v-model="form.precondition" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="执行步骤" required>
          <el-input v-model="form.steps" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="预期结果" required>
          <el-input v-model="form.expect" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="是否可自动化">
          <el-switch v-model="form.automatable" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
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
.toolbar-right {
  display: flex;
  gap: 12px;
}
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
