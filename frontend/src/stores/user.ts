import type { UserInfo } from '@/api/auth'
import { login as apiLogin } from '@/api/auth'
import { getMe } from '@/api/user'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') ?? '')
  const user = ref<UserInfo | null>(null)

  function setAuth(newToken: string, newUser: UserInfo) {
    token.value = newToken
    user.value = newUser
    localStorage.setItem('token', newToken)
  }

  async function doLogin(email: string, password: string) {
    const res = await apiLogin(email, password)
    setAuth(res.data.token, res.data.user)
  }

  async function fetchUser() {
    if (user.value) return
    const res = await getMe()
    user.value = res.data
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, setAuth, doLogin, fetchUser, logout }
})
