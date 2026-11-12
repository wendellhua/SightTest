<script setup lang="ts">
import {
  deleteAdminProject,
  deleteAdminUser,
  getPlatformSetting,
  listAdminProjects,
  listAdminUsers,
  updateAdminUser,
  updatePlatformSetting,
  type AdminProject,
  type AdminUser,
  type PlatformSetting,
} from '@/api/admin'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'

const activeTab = ref('users')

const users = ref<AdminUser[]>([])
const userTotal = ref(0)
const userPage = ref(1)
const userLoading = ref(false)

const projects = ref<AdminProject[]>([])
const projectTotal = ref(0)
const projectPage = ref(1)
const projectLoading = ref(false)

const setting = ref<PlatformSetting | null>(null)
const settingSaving = ref(false)

const statusText: Record<string, string> = { normal: '正常', frozen: '已冻结', cancelling: '注销中', cancelled: '已注销' }

async function loadUsers() {
  userLoading.value = true
  try {
    const res = await listAdminUsers({ page: userPage.value, page_size: 20 })
    users.value = res.data.items
    userTotal.value = res.data.total
  } finally {
    userLoading.value = false
  }
}

async function loadProjects() {
  projectLoading.value = true
  try {
    const res = await listAdminProjects({ page: projectPage.value, page_size: 20 })
    projects.value = res.data.items
    projectTotal.value = res.data.total
  } finally {
    projectLoading.value = false
  }
}

async function loadSetting() {
  const res = await getPlatformSetting()
  setting.value = res.data
}

async function onToggleUser(user: AdminUser) {
  const target = user.status === 'frozen' ? 'normal' : 'frozen'
  await updateAdminUser(user.id, { status: target })
  ElMessage.success(target === 'frozen' ? '已冻结' : '已启用')
  await loadUsers()
}

async function onResetPassword(user: AdminUser) {
  const { value } = await ElMessageBox.prompt(`为用户「${user.name}」设置新密码`, '重置密码', {
    inputType: 'password',
    inputValidator: (v: string) => (v && v.length >= 6 ? true : '密码至少 6 位'),
  })
  await updateAdminUser(user.id, { reset_password: value })
  ElMessage.success('密码已重置')
}

async function onDeleteUser(user: AdminUser) {
  await ElMessageBox.confirm(`确定删除用户「${user.name}」及其名下全部项目数据？`, '删除确认', { type: 'warning' })
  await deleteAdminUser(user.id)
  ElMessage.success('已删除')
  await loadUsers()
}

async function onDeleteProject(project: AdminProject) {
  await ElMessageBox.confirm(`确定删除项目「${project.name}」？`, '删除确认', { type: 'warning' })
  await deleteAdminProject(project.id)
  ElMessage.success('已删除')
  await loadProjects()
}

async function onSaveSetting() {
  if (!setting.value) return
  settingSaving.value = true
  try {
    const payload: Record<string, unknown> = {}
    for (const [k, v] of Object.entries(setting.value)) {
      if (k !== 'id' && k !== 'updated_at') payload[k] = v
    }
    await updatePlatformSetting(payload)
    ElMessage.success('平台设置已保存')
  } finally {
    settingSaving.value = false
  }
}

onMounted(() => {
  void loadUsers()
  void loadProjects()
  void loadSetting()
})
</script>

<template>
  <div class="admin-page">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="用户管理" name="users">
        <el-table v-loading="userLoading" :data="users" border>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="email" label="邮箱" min-width="200" />
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column label="角色" width="90">
            <template #default="{ row }">
              <el-tag :type="row.is_admin ? 'danger' : 'info'" size="small">{{ row.is_admin ? 'admin' : '用户' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">{{ statusText[row.status] ?? row.status }}</template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <template v-if="!row.is_admin">
                <el-button size="small" @click="onToggleUser(row)">{{ row.status === 'frozen' ? '启用' : '冻结' }}</el-button>
                <el-button size="small" @click="onResetPassword(row)">重置密码</el-button>
                <el-button size="small" type="danger" plain @click="onDeleteUser(row)">删除</el-button>
              </template>
              <span v-else>—</span>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          class="pager"
          v-model:current-page="userPage"
          :total="userTotal"
          :page-size="20"
          layout="total, prev, pager, next"
          @current-change="loadUsers"
        />
      </el-tab-pane>

      <el-tab-pane label="项目管理" name="projects">
        <el-table v-loading="projectLoading" :data="projects" border>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" min-width="160" />
          <el-table-column prop="url" label="URL" min-width="220" show-overflow-tooltip />
          <el-table-column prop="creator_id" label="创建者" width="90" />
          <el-table-column prop="plan_status" label="方案状态" width="110" />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button size="small" type="danger" plain @click="onDeleteProject(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination
          class="pager"
          v-model:current-page="projectPage"
          :total="projectTotal"
          :page-size="20"
          layout="total, prev, pager, next"
          @current-change="loadProjects"
        />
      </el-tab-pane>

      <el-tab-pane label="平台设置" name="settings">
        <el-form v-if="setting" label-width="200px" class="setting-form">
          <el-form-item label="平台总并发上限">
            <el-input-number v-model="setting.total_concurrency" :min="1" />
          </el-form-item>
          <el-form-item label="单接口压测全局上限">
            <el-input-number v-model="setting.global_stress_limit" :min="1" />
          </el-form-item>
          <el-form-item label="新用户压测上限">
            <el-input-number v-model="setting.new_user_stress_limit" :min="1" />
          </el-form-item>
          <el-form-item label="默认探索时长（分钟）">
            <el-input-number v-model="setting.default_explore_minutes" :min="1" />
          </el-form-item>
          <el-form-item label="默认探索页面数">
            <el-input-number v-model="setting.default_explore_pages" :min="1" />
          </el-form-item>
          <el-form-item label="大文件保留天数">
            <el-input-number v-model="setting.retention_days" :min="1" />
          </el-form-item>
          <el-form-item label="压测持续时长（秒）">
            <el-input-number v-model="setting.stress_duration_seconds" :min="1" />
          </el-form-item>
          <el-form-item label="每项目测试账号上限">
            <el-input-number v-model="setting.account_limit" :min="1" />
          </el-form-item>
          <el-form-item label="单账号压测并发上限">
            <el-input-number v-model="setting.default_account_stress_limit" :min="1" />
          </el-form-item>
          <el-form-item label="免责声明">
            <el-input v-model="setting.disclaimer" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="settingSaving" @click="onSaveSetting">保存设置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.setting-form {
  max-width: 640px;
}
</style>
