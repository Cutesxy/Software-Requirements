/**
 * Web Worker 管理器
 * 负责创建、管理和与 Worker 通信
 */

class WorkerManager {
  constructor() {
    this.worker = null
    this.taskId = 0
    this.pendingTasks = new Map() // 存储待处理的任务
    this.workerReady = false
    this.initPromise = null // 防止重复初始化
  }

  /**
   * 初始化 Worker
   */
  async initWorker() {
    if (this.worker && this.workerReady) {
      return Promise.resolve()
    }

    // 如果正在初始化，返回同一个 Promise
    if (this.initPromise) {
      return this.initPromise
    }

    this.initPromise = new Promise((resolve, reject) => {
      try {
        // 方案：将 Worker 文件放在 public 目录
        // 需要将 src/utils/dataProcessor.worker.js 复制到 public/dataProcessor.worker.js
        const workerPath = process.env.NODE_ENV === 'production'
          ? '/dataProcessor.worker.js'
          : '/dataProcessor.worker.js'

        this.worker = new Worker(workerPath)

        // 监听 Worker 消息
        this.worker.onmessage = (e) => {
          const { success, type, result, error, taskId } = e.data

          const task = this.pendingTasks.get(taskId)
          if (task) {
            if (success) {
              task.resolve(result)
            } else {
              task.reject(new Error(error || 'Worker processing failed'))
            }
            this.pendingTasks.delete(taskId)
          }
        }

        // 监听 Worker 错误
        this.worker.onerror = (error) => {
          console.error('Worker error:', error)
          // 清理所有待处理任务
          this.pendingTasks.forEach((task) => {
            task.reject(error)
          })
          this.pendingTasks.clear()
          this.worker = null
          this.workerReady = false
          this.initPromise = null
          reject(error)
        }

        // 监听 Worker 加载完成
        this.workerReady = true
        this.initPromise = null
        resolve()
      } catch (error) {
        console.warn('Failed to initialize Worker, falling back to main thread:', error)
        this.worker = null
        this.workerReady = false
        this.initPromise = null
        reject(error)
      }
    })

    return this.initPromise
  }

  /**
   * 发送任务到 Worker
   */
  async postTask(type, payload) {
    // 如果 Worker 未初始化，尝试初始化
    if (!this.worker) {
      try {
        await this.initWorker()
      } catch (error) {
        // Worker 初始化失败，返回 null 表示使用主线程处理
        return null
      }
    }

    // 如果 Worker 仍然不可用，返回 null
    if (!this.worker || !this.workerReady) {
      return null
    }

    return new Promise((resolve, reject) => {
      const taskId = ++this.taskId
      
      // 存储任务
      this.pendingTasks.set(taskId, { resolve, reject })

      // 设置超时（30秒）
      const timeout = setTimeout(() => {
        if (this.pendingTasks.has(taskId)) {
          this.pendingTasks.delete(taskId)
          reject(new Error('Worker task timeout'))
        }
      }, 30000)

      // 修改 resolve 以清除超时
      const originalResolve = this.pendingTasks.get(taskId).resolve
      this.pendingTasks.set(taskId, {
        resolve: (result) => {
          clearTimeout(timeout)
          originalResolve(result)
        },
        reject: (error) => {
          clearTimeout(timeout)
          reject(error)
        }
      })

      // 发送消息到 Worker
      try {
        this.worker.postMessage({
          type,
          payload: {
            ...payload,
            taskId
          }
        })
      } catch (error) {
        this.pendingTasks.delete(taskId)
        clearTimeout(timeout)
        reject(error)
      }
    })
  }

  /**
   * 终止 Worker
   */
  terminate() {
    if (this.worker) {
      // 清理所有待处理任务
      this.pendingTasks.forEach((task) => {
        task.reject(new Error('Worker terminated'))
      })
      this.pendingTasks.clear()

      this.worker.terminate()
      this.worker = null
      this.workerReady = false
      this.initPromise = null
    }
  }

  /**
   * 检查 Worker 是否可用
   */
  isAvailable() {
    return this.worker !== null && this.workerReady
  }
}

export default new WorkerManager()
