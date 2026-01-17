import { reactive } from 'vue'

// 全局提示/确认/输入（替代系统弹框）
export const uiOverlay = reactive({
  toast: {
    visible: false,
    message: '',
    type: 'info', // info|success|error
    _timer: null,
  },
  dialog: {
    visible: false,
    mode: 'confirm', // confirm|prompt
    message: '',
    input: '',
    placeholder: '',
    okText: '确定',
    cancelText: '取消',
    resolve: null,
  },
})

export function showToast(message, type = 'info', durationMs = 2000) {
  uiOverlay.toast.visible = true
  uiOverlay.toast.message = String(message ?? '')
  uiOverlay.toast.type = type

  if (uiOverlay.toast._timer) {
    clearTimeout(uiOverlay.toast._timer)
    uiOverlay.toast._timer = null
  }

  uiOverlay.toast._timer = setTimeout(() => {
    uiOverlay.toast.visible = false
    uiOverlay.toast.message = ''
  }, durationMs)
}

export function uiAlert(message, type = 'info') {
  // 用 toast 替代系统 alert
  showToast(message, type)
}

export function uiConfirm(message, { okText = '确定', cancelText = '取消' } = {}) {
  return new Promise((resolve) => {
    uiOverlay.dialog.visible = true
    uiOverlay.dialog.mode = 'confirm'
    uiOverlay.dialog.message = String(message ?? '')
    uiOverlay.dialog.input = ''
    uiOverlay.dialog.placeholder = ''
    uiOverlay.dialog.okText = okText
    uiOverlay.dialog.cancelText = cancelText
    uiOverlay.dialog.resolve = resolve
  })
}

export function uiPrompt(message, defaultValue = '', { okText = '确定', cancelText = '取消', placeholder = '' } = {}) {
  return new Promise((resolve) => {
    uiOverlay.dialog.visible = true
    uiOverlay.dialog.mode = 'prompt'
    uiOverlay.dialog.message = String(message ?? '')
    uiOverlay.dialog.input = String(defaultValue ?? '')
    uiOverlay.dialog.placeholder = String(placeholder ?? '')
    uiOverlay.dialog.okText = okText
    uiOverlay.dialog.cancelText = cancelText
    uiOverlay.dialog.resolve = resolve
  })
}

export function closeDialog(result) {
  const resolve = uiOverlay.dialog.resolve
  uiOverlay.dialog.visible = false
  uiOverlay.dialog.message = ''
  uiOverlay.dialog.resolve = null
  uiOverlay.dialog.placeholder = ''
  if (typeof resolve === 'function') resolve(result)
}


