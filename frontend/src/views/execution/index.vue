<script setup lang="ts">
import { listExecutions, startExecution, type Execution } from '@/api/execution'
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.id)

const executions = ref<Execution[]>([])
const loading = ref(false)
const scope = ref('full')
const starting = ref(false)

const scopeText: Record<string, string> = { full: '全量', func: '功能', api: '接口', perf: '性能', mech: '机制' }
const statusText: Record<string, string> = {
  queued: '排队中',
  running: '运行中',
  completed: '已完成',
  failed: '失败',
  terminated: '已终止',
}

async function load() {
  loading.value = true
  try {
    const res = await listExecutions(projectId, { page: 1, page_size: 50 })
    executions.value = res.data.items
  } finally {
    loading.value = false
  }
}

async function onStart() {
  starting.value = true
  try {
    const res = await startExecution(projectId, { scope: scope.value })
    ElMessage.success('测试执行已启动')
    router.push(`/project/${projectId}/execution/${res.data.execution_id}`)
  } finally {
    starting.value = false
  }
}

function openDetail(e: Execution) {
  router.push(`/project/${projectId}/execution/${e.id}`)
}

onMounted(load)
</script>

<template>
  <div class="execution-page">
    <el-card class="start-card">
      <div class="start-row">
        <span class="label">发起测试执行：</span>
        <el-select v-model="scope" style="width: 160px">
          <el-option v-for="(text, key) in scopeText" :key="key" :label="text" :value="key" />
        </el-select>
        <el-button type="primary" :loading="starting" @click="onStart">开始执行</el-button>
      </div>
    </el-card>

    <el-card class="list-card">
      <template #header><span class="title">执行记录</span></template>
      <el-table v-loading="loading" :data="executions" border>
        <el-table-column prop="name" label="名称" min-width="160" />
        <el-table-column label="范围" width="90">
          <template #default="{ row }">{{ scopeText[row.scope] ?? row.scope }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'running' ? 'warning' : row.status === 'failed' ? 'danger' : 'info'" size="small">
              {{ statusText[row.status] ?? row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进度" width="160">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" :stroke-width="12" />
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.start-card {
  margin-bottom: 20px;
}
.start-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.label {
  font-weight: 600;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
</style>
