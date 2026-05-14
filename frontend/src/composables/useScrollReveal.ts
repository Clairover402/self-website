import { onMounted, onUnmounted, type Ref } from 'vue'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export interface SectionConfig {
  ref: Ref<HTMLElement | null>
  childSelector?: string
  stagger?: number
  y?: number
  start?: string
  onEnter?: () => void
}

export function useScrollReveal(sections: SectionConfig[]) {
  const mm = gsap.matchMedia()

  onMounted(() => {
    mm.add('(prefers-reduced-motion: no-preference)', () => {
      sections.forEach((config) => {
        const el = config.ref.value
        if (!el) return

        gsap.fromTo(
          el,
          { opacity: 0, y: config.y ?? 60 },
          {
            opacity: 1,
            y: 0,
            duration: 0.7,
            ease: 'power2.out',
            scrollTrigger: {
              trigger: el,
              start: config.start ?? 'top 82%',
              toggleActions: 'restart none restart none',
              onEnter: () => config.onEnter?.(),
            },
          },
        )

        if (config.childSelector) {
          const children = gsap.utils.toArray(config.childSelector, el)
          if (children.length) {
            gsap.fromTo(
              children,
              { opacity: 0, y: 40 },
              {
                opacity: 1,
                y: 0,
                duration: 0.5,
                stagger: config.stagger ?? 0.15,
                ease: 'power2.out',
                scrollTrigger: {
                  trigger: el,
                  start: config.start ?? 'top 82%',
                  toggleActions: 'restart none restart none',
                },
              },
            )
          }
        }
      })
    })
  })

  onUnmounted(() => {
    mm.revert()
  })
}
