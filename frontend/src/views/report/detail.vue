<script setup lang="ts">
import { downloadReportPdf, getReport, type Report } from '@/api/report'
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const projectId = Number(route.params.id)
const reportId = Number(route.params.reportId)

const report = ref<Report | null>(null)
let timer: number | undefined

const riskText: Record<string, string> = { high: '高', medium: '中', low: '低' }

async function load() {
  const res = await getReport(projectId, reportId)
  report.value = res.data
  if (res.data.status === 'generating' && !timer) {
    timer = window.setInterval(async () => {
      const r = await getReport(projectId, reportId)
      report.value = r.data
      if (r.data.status !== 'generating') {
        window.clearInterval(timer)
        timer = undefined
      }
    }, 2000)
  }
}

async function onExport() {
  const blob = await downloadReportPdf(projectId, reportId)
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `report_${reportId}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(load)
onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <div class="report-detail" v-if="report">
    <el-card class="head-card">
      <div class="head">
        <h2 class="name">测试报告 #{{ report.id }}</h2>
        <el-button :disabled="report.status !== 'completed'" @click="onExport">导出</el-button>
      </div>

      <el-row :gutter="16" class="conclusion">
        <el-col :span="8">
          <div class="metric">
            <div class="metric-value">{{ report.score }}</div>
            <div class="metric-label">综合评分</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="metric">
            <div class="metric-value">
              <el-tag :type="report.risk_level === 'high' ? 'danger' : report.risk_level === 'medium' ? 'warning' : 'success'">
                {{ riskText[report.risk_level] ?? report.risk_level }}
              </el-tag>
            </div>
            <div class="metric-label">风险等级</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="metric">
            <div class="metric-value">{{ report.status === 'completed' ? '已生成' : '生成中…' }}</div>
            <div class="metric-label">状态</div>
          </div>
        </el-col>
      </el-row>

      <div class="summary">
        <div class="summary-label">结论摘要</div>
        <div class="summary-text">{{ report.summary ?? '摘要生成中…' }}</div>
      </div>
    </el-card>

    <el-card class="section">
      <template #header><span class="title">主要问题（{{ report.top_issues?.length ?? 0 }}）</span></template>
      <el-table :data="report.top_issues ?? []" border>
        <el-table-column label="类型" width="90">
          <template #default="{ row }">{{ row.type === 'case' ? '不通过用例' : '主动发现' }}</template>
        </el-table-column>
        <el-table-column label="内容" min-width="300">
          <template #default="{ row }">{{ row.name ?? row.description }}</template>
        </el-table-column>
        <el-table-column label="优先级/严重度" width="120">
          <template #default="{ row }">{{ row.priority ?? row.severity ?? '—' }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.report-detail {
  max-width: 900px;
  margin: 0 auto;
}
.head-card {
  margin-bottom: 20px;
}
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.name {
  font-size: 20px;
  margin: 0;
}
.conclusion {
  margin-top: 24px;
}
.metric {
  text-align: center;
  padding: 16px;
  background: var(--st-bg);
  border-radius: 8px;
}
.metric-value {
  font-size: 28px;
  font-weight: 700;
}
.metric-label {
  color: var(--st-text-2);
  margin-top: 4px;
}
.summary {
  margin-top: 24px;
}
.summary-label {
  font-weight: 600;
  margin-bottom: 8px;
}
.summary-text {
  color: var(--st-text);
  line-height: 1.6;
}
.section {
  margin-bottom: 20px;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
</style>
