<script setup lang="ts">
import {
  getExecution,
  listCaseExecutions,
  listIssues,
  terminateExecution,
  updateIssue,
  type CaseExecution,
  type Execution,
  type Issue,
} from '@/api/execution'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const projectId = Number(route.params.id)
const executionId = Number(route.params.executionId)

const execution = ref<Execution | null>(null)
const caseExecutions = ref<CaseExecution[]>([])
const issues = ref<Issue[]>([])
let timer: number | undefined

const resultText: Record<string, string> = { pass: '通过', fail: '失败', blocked: '阻塞' }
const severityText: Record<string, string> = { high: '高', medium: '中', low: '低' }

async function load() {
  const [e, c, i] = await Promise.all([
    getExecution(projectId, executionId),
    listCaseExecutions(projectId, executionId),
    listIssues(projectId, { page: 1, page_size: 200 }),
  ])
  execution.value = e.data
  caseExecutions.value = c.data
  issues.value = i.data.items.filter((x) => x.execution_id === executionId)

  if (['queued', 'running'].includes(e.data.status)) {
    startPolling()
  } else if (timer) {
    window.clearInterval(timer)
    timer = undefined
  }
}

function startPolling() {
  if (timer) return
  timer = window.setInterval(async () => {
    const res = await getExecution(projectId, executionId)
    execution.value = res.data
    if (['completed', 'failed', 'terminated'].includes(res.data.status)) {
      window.clearInterval(timer)
      timer = undefined
      await load()
    }
  }, 2000)
}

async function onTerminate() {
  await ElMessageBox.confirm('确定终止当前执行？', '终止确认', { type: 'warning' })
  await terminateExecution(projectId, executionId)
  ElMessage.success('已终止')
  await load()
}

async function onMarkMisreport(issue: Issue) {
  await ElMessageBox.confirm('将该问题标记为误报？后续同类问题将自动忽略。', '标记误报', { type: 'warning' })
  await updateIssue(projectId, issue.id, 'misreported')
  ElMessage.success('已标记')
  await load()
}

onMounted(load)
onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <div class="execution-detail" v-if="execution">
    <el-card class="head-card">
      <div class="head">
        <div>
          <div class="name">
            {{ execution.name }}
            <el-tag v-if="execution.is_debug" size="small" type="info">调试</el-tag>
          </div>
          <div class="meta">版本 {{ execution.plan_version_no }} · {{ new Date(execution.created_at).toLocaleString() }}</div>
        </div>
        <el-button v-if="['queued', 'running'].includes(execution.status)" size="small" type="danger" plain @click="onTerminate">
          终止
        </el-button>
      </div>
      <el-progress
        class="progress"
        :percentage="execution.progress"
        :status="execution.status === 'completed' ? 'success' : execution.status === 'failed' ? 'exception' : ''"
      />
    </el-card>

    <el-card class="section">
      <template #header><span class="title">用例执行结果（{{ caseExecutions.length }}）</span></template>
      <el-table :data="caseExecutions" border>
        <el-table-column label="用例名称" min-width="180">
          <template #default="{ row }">{{ row.case_snapshot?.name ?? `#${row.case_id}` }}</template>
        </el-table-column>
        <el-table-column label="结果" width="90">
          <template #default="{ row }">
            <el-tag :type="row.result === 'pass' ? 'success' : row.result === 'fail' ? 'danger' : 'info'" size="small">
              {{ resultText[row.result] ?? row.result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="判定理由" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">{{ (row.evidence as Record<string, unknown>)?.reason ?? '—' }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="section">
      <template #header><span class="title">主动发现的问题（{{ issues.length }}）</span></template>
      <el-table :data="issues" border>
        <el-table-column label="页面" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.page }}</template>
        </el-table-column>
        <el-table-column label="严重度" width="90">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'high' ? 'danger' : row.severity === 'medium' ? 'warning' : 'info'" size="small">
              {{ severityText[row.severity] ?? row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="问题描述" min-width="240" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'open' ? 'danger' : 'success'" size="small">
              {{ row.status === 'open' ? '待处理' : '误报' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button v-if="row.status === 'open'" size="small" type="warning" plain @click="onMarkMisreport(row)">
              标记误报
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.execution-detail {
  max-width: 960px;
  margin: 0 auto;
}
.head-card {
  margin-bottom: 20px;
}
.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}
.name {
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}
.meta {
  color: var(--st-text-2);
  font-size: 13px;
  margin-top: 4px;
}
.progress {
  margin-top: 16px;
}
.section {
  margin-bottom: 20px;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
</style>
