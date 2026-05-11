import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

interface SEOMeta {
  title: string
  description: string
  keywords: string
  ogTitle: string
  ogDescription: string
  ogImage: string
  ogUrl: string
}

const defaultMeta: SEOMeta = {
  title: '全栈开发者个人网站',
  description: '全栈开发者技术博客与作品集网站，分享前端、后端、AI 等技术领域的实战经验。',
  keywords: '全栈开发, Vue, React, Python, FastAPI, TypeScript, 技术博客',
  ogTitle: '全栈开发者个人网站',
  ogDescription: '全栈开发者技术博客与作品集网站',
  ogImage: '/og-image.png',
  ogUrl: 'https://example.com'
}

export function useSEO(customMeta: Partial<SEOMeta> = {}) {
  const route = useRoute()
  const meta = { ...defaultMeta, ...customMeta }

  const updateMeta = () => {
    document.title = meta.title

    const metaTags = {
      'description': meta.description,
      'keywords': meta.keywords,
      'og:title': meta.ogTitle,
      'og:description': meta.ogDescription,
      'og:image': meta.ogImage,
      'og:url': meta.ogUrl,
      'twitter:card': 'summary_large_image',
      'twitter:title': meta.ogTitle,
      'twitter:description': meta.ogDescription,
    }

    Object.entries(metaTags).forEach(([name, content]) => {
      let element = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`) as HTMLMetaElement

      if (!element) {
        element = document.createElement('meta')
        if (name.startsWith('og:') || name.startsWith('twitter:')) {
          element.setAttribute('property', name)
        } else {
          element.setAttribute('name', name)
        }
        document.head.appendChild(element)
      }
      element.setAttribute('content', content)
    })
  }

  watch(() => route.path, updateMeta, { immediate: true })

  return { meta, updateMeta }
}

export function useStructuredData(type: string, data: object) {
  const jsonLd = ref({
    '@context': 'https://schema.org',
    '@type': type,
    ...data
  })

  const updateStructuredData = () => {
    let script = document.querySelector('script[type="application/ld+json"]') as HTMLScriptElement

    if (!script) {
      script = document.createElement('script')
      script.type = 'application/ld+json'
      document.head.appendChild(script)
    }

    script.textContent = JSON.stringify(jsonLd.value)
  }

  watch(jsonLd, updateStructuredData, { immediate: true, deep: true })

  return { jsonLd }
}
