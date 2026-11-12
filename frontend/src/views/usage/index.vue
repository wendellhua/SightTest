<script setup lang="ts">
import { listProjects, type Project } from '@/api/project'
import { getUsage, type UsageResult } from '@/api/usage'
import { onMounted, ref } from 'vue'

const usage = ref<UsageResult>({
  overview: { input_tokens: 0, output_tokens: 0, total_cost: 0, cost_unknown: false, project_count: 0 },
  by_project: [],
  by_model: [],
  by_task: [],
})
const projects = ref<Project[]>([])
const days = ref(30)
const projectId = ref<number | null>(null)
const loading = ref(false)

function formatTokens(n: number) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return `${n}`
}

function formatCost(cost: number | null | undefined) {
  if (cost === null || cost === undefined) return '暂无价格'
  return `¥${cost.toFixed(2)}`
}

async function load() {
  loading.value = true
  try {
    const res = await getUsage({ project_id: projectId.value ?? undefined, days: days.value })
    usage.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const res = await listProjects(1, 100)
  projects.value = res.data.items
  await load()
})
</script>

<template>
  <div class="usage-page">
    <el-card class="filter-card">
      <div class="filter-row">
        <span class="label">统计范围：</span>
        <el-select v-model="days" style="width: 140px" @change="load">
          <el-option label="近 7 天" :value="7" />
          <el-option label="近 30 天" :value="30" />
          <el-option label="近 90 天" :value="90" />
        </el-select>
        <el-select v-model="projectId" clearable placeholder="全部项目" style="width: 200px" @change="load">
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>
    </el-card>

    <el-card class="overview-card" v-loading="loading">
      <el-row :gutter="16">
        <el-col :span="6">
          <div class="metric">
            <div class="value">{{ formatTokens(usage.overview.input_tokens) }}</div>
            <div class="label">输入 token</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric">
            <div class="value">{{ formatTokens(usage.overview.output_tokens) }}</div>
            <div class="label">输出 token</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric">
            <div class="value accent">¥{{ usage.overview.total_cost.toFixed(2) }}</div>
            <div class="label">总成本（元）</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric">
            <div class="value">{{ usage.overview.project_count }}</div>
            <div class="label">项目数</div>
          </div>
        </el-col>
      </el-row>
      <el-alert
        v-if="usage.overview.cost_unknown"
        type="info"
        :closable="false"
        show-icon
        title="部分模型暂无内置价格，总成本仅统计已计价的部分"
        style="margin-top: 16px"
      />
    </el-card>

    <el-tabs class="detail-tabs" v-loading="loading">
      <el-tab-pane label="按项目" name="project">
        <el-table :data="usage.by_project" border>
          <el-table-column prop="project_name" label="项目" min-width="180" />
          <el-table-column label="输入 token" width="140">
            <template #default="{ row }">{{ formatTokens(row.input_tokens) }}</template>
          </el-table-column>
          <el-table-column label="输出 token" width="140">
            <template #default="{ row }">{{ formatTokens(row.output_tokens) }}</template>
          </el-table-column>
          <el-table-column label="成本" width="140">
            <template #default="{ row }">
              {{ formatCost(row.cost) }}<span v-if="row.cost_unknown" class="unknown">*</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="按模型" name="model">
        <el-table :data="usage.by_model" border>
          <el-table-column prop="model" label="模型" min-width="200" />
          <el-table-column label="输入 token" width="140">
            <template #default="{ row }">{{ formatTokens(row.input_tokens) }}</template>
          </el-table-column>
          <el-table-column label="输出 token" width="140">
            <template #default="{ row }">{{ formatTokens(row.output_tokens) }}</template>
          </el-table-column>
          <el-table-column label="成本" width="140">
            <template #default="{ row }">{{ formatCost(row.cost) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="按任务" name="task">
        <el-table :data="usage.by_task" border>
          <el-table-column prop="name" label="任务" min-width="200" />
          <el-table-column label="输入 token" width="140">
            <template #default="{ row }">{{ formatTokens(row.input_tokens) }}</template>
          </el-table-column>
          <el-table-column label="输出 token" width="140">
            <template #default="{ row }">{{ formatTokens(row.output_tokens) }}</template>
          </el-table-column>
          <el-table-column label="成本" width="140">
            <template #default="{ row }">
              {{ formatCost(row.cost) }}<span v-if="row.cost_unknown" class="unknown">*</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.filter-card {
  margin-bottom: 20px;
}
.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.label {
  font-weight: 600;
}
.overview-card {
  margin-bottom: 20px;
}
.metric {
  text-align: center;
  padding: 16px;
  background: var(--st-bg);
  border-radius: 8px;
}
.value {
  font-size: 26px;
  font-weight: 700;
}
.value.accent {
  color: var(--el-color-primary);
}
.label {
  color: var(--st-text-2);
  margin-top: 4px;
  font-weight: 400;
}
.unknown {
  color: var(--el-color-warning);
  margin-left: 2px;
}
</style>
