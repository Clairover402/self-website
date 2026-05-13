import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isLightTheme = ref(false)

  function initTheme() {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      isLightTheme.value = savedTheme === 'light'
    } else {
      isLightTheme.value = window.matchMedia('(prefers-color-scheme: light)').matches
    }
    applyTheme()
  }

  function toggleTheme() {
    isLightTheme.value = !isLightTheme.value
    localStorage.setItem('theme', isLightTheme.value ? 'light' : 'dark')
    applyTheme()
  }

  function applyTheme() {
    if (isLightTheme.value) {
      document.documentElement.classList.remove('dark')
    } else {
      document.documentElement.classList.add('dark')
    }
  }

  return {
    isLightTheme,
    initTheme,
    toggleTheme,
    applyTheme
  }
})
