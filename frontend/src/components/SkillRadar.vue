<template>
  <div ref="chartRef" class="w-full h-80 sm:h-96"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useThemeStore } from '@/stores/theme'

interface Skill {
  name: string
  value: number
}

const props = defineProps<{
  skills: Skill[]
}>()

const themeStore = useThemeStore()
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

function isDark() {
  return document.documentElement.classList.contains('dark')
}

function getOption(): echarts.EChartsOption {
  const dark = isDark()
  const axisNameColor = dark ? '#94a3b8' : '#64748b'
  const splitLineColor = dark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)'
  const axisLineColor = dark ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)'
  const areaColors = dark
    ? ['rgba(14, 165, 233, 0.02)', 'rgba(14, 165, 233, 0.04)']
    : ['rgba(14, 165, 233, 0.04)', 'rgba(14, 165, 233, 0.08)']

  return {
    radar: {
      center: ['50%', '55%'],
      radius: '65%',
      indicator: props.skills.map((s) => ({ name: s.name, max: 100 })),
      axisName: { color: axisNameColor, fontSize: 12 },
      splitArea: { areaStyle: { color: areaColors } },
      splitLine: { lineStyle: { color: splitLineColor } },
      axisLine: { lineStyle: { color: axisLineColor } },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: props.skills.map((s) => s.value),
            name: '技能',
            areaStyle: {
              color: {
                type: 'radial',
                x: 0.5, y: 0.5, r: 0.5,
                colorStops: [
                  { offset: 0, color: 'rgba(217, 70, 239, 0.3)' },
                  { offset: 1, color: 'rgba(14, 165, 233, 0.15)' },
                ],
              },
            },
            lineStyle: { color: '#d946ef', width: 2 },
            itemStyle: { color: '#0ea5e9' },
          },
        ],
      },
    ],
  }
}

function initChart() {
  if (!chartRef.value) return
  if (chart) chart.dispose()
  chart = echarts.init(chartRef.value)
  chart.setOption(getOption())
}

function handleResize() {
  chart?.resize()
}

watch(() => themeStore.isLightTheme, () => {
  if (chart) {
    chart.setOption(getOption(), true)
  }
})

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>