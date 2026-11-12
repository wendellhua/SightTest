<script setup lang="ts">
import { listExecutions, type Execution } from '@/api/execution'
import { createReport, listReports, type Report } from '@/api/report'
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const projectId = Number(route.params.id)

const reports = ref<Report[]>([])
const executions = ref<Execution[]>([])
const loading = ref(false)
const scope = ref('snapshot')
const executionId = ref<number | null>(null)
const generating = ref(false)

const riskText: Record<string, string> = { high: '高', medium: '中', low: '低' }

async function load() {
  loading.value = true
  try {
    const [r, e] = await Promise.all([
      listReports(projectId, { page: 1, page_size: 50 }),
      listExecutions(projectId, { page: 1, page_size: 50 }),
    ])
    reports.value = r.data.items
    executions.value = e.data.items.filter((x) => !x.is_debug)
  } finally {
    loading.value = false
  }
}

async function onCreate() {
  if (scope.value === 'execution' && !executionId.value) {
    ElMessage.warning('请选择执行记录')
    return
  }
  generating.value = true
  try {
    const res = await createReport(projectId, {
      scope: scope.value,
      execution_id: scope.value === 'execution' ? executionId.value : null,
    })
    ElMessage.success('报告生成中')
    router.push(`/project/${projectId}/report/${res.data.report_id}`)
  } finally {
    generating.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="report-page">
    <el-card class="gen-card">
      <div class="gen-row">
        <span class="label">生成测试报告：</span>
        <el-radio-group v-model="scope">
          <el-radio-button value="snapshot">项目当前状态</el-radio-button>
          <el-radio-button value="execution">某次执行</el-radio-button>
        </el-radio-group>
        <el-select
          v-if="scope === 'execution'"
          v-model="executionId"
          placeholder="选择执行记录"
          style="width: 220px"
        >
          <el-option v-for="e in executions" :key="e.id" :label="`${e.name}（${e.created_at.slice(0, 16).replace('T', ' ')}）`" :value="e.id" />
        </el-select>
        <el-button type="primary" :loading="generating" @click="onCreate">生成报告</el-button>
      </div>
    </el-card>

    <el-card class="list-card">
      <template #header><span class="title">报告列表</span></template>
      <el-table v-loading="loading" :data="reports" border>
        <el-table-column prop="id" label="编号" width="90" />
        <el-table-column label="范围" width="120">
          <template #default="{ row }">{{ row.scope === 'execution' ? '某次执行' : '当前状态' }}</template>
        </el-table-column>
        <el-table-column prop="score" label="评分" width="90" />
        <el-table-column label="风险等级" width="100">
          <template #default="{ row }">
            <el-tag :type="row.risk_level === 'high' ? 'danger' : row.risk_level === 'medium' ? 'warning' : 'success'" size="small">
              {{ riskText[row.risk_level] ?? row.risk_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'danger' : 'info'" size="small">
              {{ row.status === 'completed' ? '已生成' : row.status === 'failed' ? '失败' : '生成中' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="生成时间" min-width="170">
          <template #default="{ row }">{{ new Date(row.created_at).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="router.push(`/project/${projectId}/report/${row.id}`)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.gen-card {
  margin-bottom: 20px;
}
.gen-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.label {
  font-weight: 600;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
</style>
