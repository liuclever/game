import noneImageUrl from '@/assets/images/none.jpg'

// 兼容多格式本地资源：gif/png/jpg/jpeg/webp
// 重要：Vite 只会打包 glob 命中的文件；所以必须把所有可能后缀都加进来。
// 同时兼容两类目录：
// - src/assets/handbook/（图鉴专用）
// - src/assets/images/（项目里其他功能已在使用的图片目录）
//
// 额外兼容：
// - 资源文件可能是 image{ID}.gif/png...（项目既有命名）
// - 配置里可能写 pet{ID}（图鉴模块命名）
const imageModules = {
  // handbook 目录：兼容 pet{id} 与 image{id} 两种命名
  ...import.meta.glob('@/assets/handbook/pet*.gif', { eager: true }),
  ...import.meta.glob('@/assets/handbook/pet*.png', { eager: true }),
  ...import.meta.glob('@/assets/handbook/pet*.jpg', { eager: true }),
  ...import.meta.glob('@/assets/handbook/pet*.jpeg', { eager: true }),
  ...import.meta.glob('@/assets/handbook/pet*.webp', { eager: true }),
  ...import.meta.glob('@/assets/handbook/image*.gif', { eager: true }),
  ...import.meta.glob('@/assets/handbook/image*.png', { eager: true }),
  ...import.meta.glob('@/assets/handbook/image*.jpg', { eager: true }),
  ...import.meta.glob('@/assets/handbook/image*.jpeg', { eager: true }),
  ...import.meta.glob('@/assets/handbook/image*.webp', { eager: true }),

  // images 目录（项目既有目录）
  ...import.meta.glob('@/assets/images/pet*.gif', { eager: true }),
  ...import.meta.glob('@/assets/images/pet*.png', { eager: true }),
  ...import.meta.glob('@/assets/images/pet*.jpg', { eager: true }),
  ...import.meta.glob('@/assets/images/pet*.jpeg', { eager: true }),
  ...import.meta.glob('@/assets/images/pet*.webp', { eager: true }),
  ...import.meta.glob('@/assets/images/image*.gif', { eager: true }),
  ...import.meta.glob('@/assets/images/image*.png', { eager: true }),
  ...import.meta.glob('@/assets/images/image*.jpg', { eager: true }),
  ...import.meta.glob('@/assets/images/image*.jpeg', { eager: true }),
  ...import.meta.glob('@/assets/images/image*.webp', { eager: true }),
}

const localKeyVariants = (localKey) => {
  const key = String(localKey || '').trim()
  if (!key) return []

  const out = []
  const push = (v) => {
    const s = String(v || '').trim()
    if (!s) return
    if (!out.includes(s)) out.push(s)
  }

  push(key)

  const m = key.match(/^(.*?)(?:\.([^.]+))?$/)
  const base = (m && m[1]) || key
  const ext = (m && m[2]) || ''

  const petMatch = base.match(/^pet(\d+)$/i)
  const imageMatch = base.match(/^image(\d+)$/i)

  if (petMatch) {
    const id = petMatch[1]
    push(`image${id}`)
    if (ext) push(`image${id}.${ext}`)
  }
  if (imageMatch) {
    const id = imageMatch[1]
    push(`pet${id}`)
    if (ext) push(`pet${id}.${ext}`)
  }

  return out
}

const resolveLocalImage = (localKey) => {
  // local_key 允许：pet2 / pet2.gif / image2 / image2.png 等
  const variants = localKeyVariants(localKey)
  if (!variants.length) return ''

  const tryPaths = []
  for (const v of variants) {
    const basePaths = [
      `/src/assets/handbook/${v}`,
      `/src/assets/images/${v}`,
    ]
    for (const basePath of basePaths) {
      if (v.includes('.')) {
        tryPaths.push(basePath)
        continue
      }
      for (const ext of ['gif', 'png', 'jpg', 'jpeg', 'webp']) {
        tryPaths.push(`${basePath}.${ext}`)
      }
    }
  }

  for (const p of tryPaths) {
    const mod = imageModules[p]
    if (!mod) continue
    return mod.default || mod || ''
  }

  // public 静态路径：仅当 local_key 显式给出路径时启用（避免猜测导致大量 404）。
  const first = variants[0]
  if (first && first.startsWith('public/')) {
    return `/${first.replace(/^public\//, '')}`
  }
  if (
    first &&
    first.includes('/') &&
    (first.endsWith('.gif') || first.endsWith('.png') || first.endsWith('.jpg') || first.endsWith('.jpeg') || first.endsWith('.webp'))
  ) {
    return `/${first}`
  }
  return ''
}

export function resolveHandbookImage(image, fallback = noneImageUrl) {
  if (!image) return fallback
  if (image.type === 'url') return image.url || fallback
  return resolveLocalImage(image.local_key) || fallback
}


