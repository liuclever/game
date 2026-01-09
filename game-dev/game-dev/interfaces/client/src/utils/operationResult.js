/**
 * 操作结果页面跳转工具函数
 * 用于替代 Toast 提示，跳转到结果页面显示操作结果
 * 
 * 使用方法：
 * import { useOperationResult } from '@/utils/operationResult'
 * const { showSuccess, showError, showInfo } = useOperationResult()
 */

import { useRouter } from 'vue-router'

/**
 * useOperationResult composable
 * 在组件中使用：const { showSuccess, showError, showInfo } = useOperationResult()
 */
export const useOperationResult = () => {
  const router = useRouter()

  /**
   * 跳转到操作成功页面
   * @param {Object} options - 配置选项
   * @param {string} options.title - 标题，默认"操作成功"
   * @param {string} options.message - 主要消息
   * @param {string} options.detail - 详细信息（可选）
   * @param {string} options.backPath - 返回路径，默认"/"
   * @param {string} options.backText - 返回按钮文字，默认"返回"
   * @param {boolean} options.showHome - 是否显示返回首页按钮，默认true
   */
  const showSuccess = (options = {}) => {
    router.push({
      path: '/operation/result',
      query: {
        success: 'true',
        title: options.title || '操作成功',
        message: options.message || '操作已成功完成',
        detail: options.detail || '',
        backPath: options.backPath || '/',
        backText: options.backText || '返回',
        showHome: options.showHome !== false ? 'true' : 'false',
      }
    })
  }

  /**
   * 跳转到操作失败页面
   * @param {Object} options - 配置选项
   * @param {string} options.title - 标题，默认"操作失败"
   * @param {string} options.message - 主要消息（错误信息）
   * @param {string} options.detail - 详细信息（可选）
   * @param {string} options.backPath - 返回路径，默认"/"
   * @param {string} options.backText - 返回按钮文字，默认"返回"
   * @param {boolean} options.showHome - 是否显示返回首页按钮，默认true
   */
  const showError = (options = {}) => {
    router.push({
      path: '/operation/result',
      query: {
        success: 'false',
        title: options.title || '操作失败',
        message: options.message || '操作失败，请稍后重试',
        detail: options.detail || '',
        backPath: options.backPath || '/',
        backText: options.backText || '返回',
        showHome: options.showHome !== false ? 'true' : 'false',
      }
    })
  }

  /**
   * 显示信息提示页面（用于信息类提示，不是错误也不是成功）
   * @param {Object} options - 配置选项
   */
  const showInfo = (options = {}) => {
    router.push({
      path: '/operation/result',
      query: {
        success: 'true', // 信息提示也用成功样式
        title: options.title || '提示',
        message: options.message || '',
        detail: options.detail || '',
        backPath: options.backPath || '/',
        backText: options.backText || '返回',
        showHome: options.showHome !== false ? 'true' : 'false',
      }
    })
  }

  return {
    showSuccess,
    showError,
    showInfo,
  }
}
