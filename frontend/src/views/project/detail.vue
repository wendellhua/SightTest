<script setup lang="ts">
import { getBuild, listVersions, startBuild, terminateBuild, type Build, type PlanVersion } from '@/api/build'
import { getProjectDashboard, type CaseStats, type ProjectDashboard } from '@/api/dashboard'
import { getProject, type Project } from '@/api/project'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const projectId = Number(route.params.id)

const project = ref<Project | null>(null)
const versions = ref<PlanVersion[]>([])
const building = ref<Build | null>(null)
const dashboard = ref<ProjectDashboard | null>(null)
const starting = ref(false)
let timer: number | undefined

const caseTypeText: Record<string, string> = { func: '功能', api: '接口', perf: '性能', mech: '机制' }
const caseTypeRows = computed(() => {
  const stats = dashboard.value?.case_stats ?? {}
  return Object.entries(stats).map(([key, value]: [string, CaseStats]) => ({
    type: caseTypeText[key] ?? key,
    total: value.total,
    pass: value.pass,
    fail: value.fail,
    blocked: value.blocked,
    none: value.none,
  }))
})

const statusText: Record<string, string> = {
  empty: '无方案',
  building: '建设中',
  ready: '已就绪',
  build_failed: '建设失败',
}

async function load() {
  const [p, v] = await Promise.all([getProject(projectId), listVersions(projectId)])
  project.value = p.data
  versions.value = v.data
  const d = await getProjectDashboard(projectId)
  dashboard.value = d.data
  if (p.data.plan_status === 'building') {
    const active = v.data.find((x) => x.status === 'building')
    if (active) await poll(active.id)
  }
}

async function onStart() {
  starting.value = true
  try {
    const res = await startBuild(projectId)
    ElMessage.success('方案建设已启动')
    await poll(res.data.build_id)
  } finally {
    starting.value = false
  }
}

async function poll(buildId: number) {
  if (timer) window.clearInterval(timer)
  const tick = async () => {
    const res = await getBuild(projectId, buildId)
    building.value = res.data
    if (['completed', 'failed', 'terminated'].includes(res.data.status)) {
      if (timer) window.clearInterval(timer)
      timer = undefined
      if (res.data.status === 'completed') ElMessage.success('方案建设完成')
      else ElMessage.warning('方案建设已结束')
      await load()
    }
  }
  await tick()
  timer = window.setInterval(tick, 2000)
}

async function onTerminate() {
  if (!building.value) return
  await ElMessageBox.confirm('确定终止当前方案建设？', '终止确认', { type: 'warning' })
  await terminateBuild(projectId, building.value.build_id)
  ElMessage.success('已终止')
  await load()
}

onMounted(load)
onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <div class="project-detail" v-if="project">
    <el-card class="head-card">
      <div class="head">
        <div>
          <div class="name">{{ project.name }}</div>
          <div class="url">{{ project.url }}</div>
        </div>
        <el-tag :type="project.plan_status === 'ready' ? 'success' : 'info'">
          {{ statusText[project.plan_status] ?? project.plan_status }}
        </el-tag>
      </div>

      <div v-if="building" class="build-panel">
        <el-progress :percentage="building.progress" :status="building.status === 'building' ? '' : 'success'" />
        <div class="build-stage">
          <span>当前阶段：{{ building.stage ?? '准备中' }}</span>
          <el-button size="small" type="danger" plain @click="onTerminate">终止建设</el-button>
        </div>
      </div>

      <div v-else class="build-actions">
        <el-button type="primary" :loading="starting" :disabled="!project.model_config_id" @click="onStart">
          {{ project.plan_status === 'ready' ? '重新探索' : '启动方案建设' }}
        </el-button>
        <el-button :disabled="project.plan_status !== 'ready'" @click="$router.push(`/project/${project.id}/cases`)">
          用例管理
        </el-button>
        <el-button :disabled="project.plan_status !== 'ready'" @click="$router.push(`/project/${project.id}/executions`)">
          测试执行
        </el-button>
        <el-button :disabled="project.plan_status !== 'ready'" @click="$router.push(`/project/${project.id}/reports`)">
          测试报告
        </el-button>
        <span v-if="!project.model_config_id" class="hint">请先在「模型配置」中绑定模型</span>
      </div>
    </el-card>

    <el-card class="list-card">
      <template #header><span class="title">测试状态总览</span></template>
      <div v-if="dashboard" class="dash-meta">
        <span>运行状态：<b>{{ dashboard.run_status === 'running' ? '运行中' : '空闲' }}</b></span>
        <span>待处理问题：<b>{{ dashboard.issue_stats.open }}</b></span>
      </div>
      <el-table v-if="dashboard" :data="caseTypeRows" border>
        <el-table-column prop="type" label="类型" width="90" />
        <el-table-column prop="total" label="总数" />
        <el-table-column prop="pass" label="通过" />
        <el-table-column prop="fail" label="失败" />
        <el-table-column prop="blocked" label="阻塞" />
        <el-table-column prop="none" label="未执行" />
      </el-table>
    </el-card>

    <el-card class="list-card">
      <template #header><span class="title">方案版本</span></template>
      <el-table :data="versions" border>
        <el-table-column prop="version_no" label="版本号" width="100" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'completed' ? 'success' : row.status === 'building' ? 'warning' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="统计" min-width="180">
          <template #default="{ row }">
            <span v-if="row.explore_stats">
              页面 {{ row.explore_stats.pages }} · 模块 {{ row.explore_stats.modules }} · 用例 {{ row.explore_stats.cases }}
            </span>
            <span v-else>—</span>
          </template>
        </el-table-column>
        <el-table-column label="开始时间" min-width="170">
          <template #default="{ row }">{{ new Date(row.started_at).toLocaleString() }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.project-detail {
  max-width: 900px;
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
  font-size: 20px;
  font-weight: 600;
}
.url {
  color: var(--st-text-2);
  margin-top: 4px;
}
.build-panel {
  margin-top: 20px;
}
.build-stage {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
  color: var(--st-text-2);
}
.build-actions {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.hint {
  color: var(--st-text-2);
  font-size: 13px;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
.dash-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
  color: var(--st-text-2);
}
</style>
