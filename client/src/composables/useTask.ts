import { ref } from 'vue'
import { createTask, getTask, listTasks, cancelTask, type Task } from '../api/client'

const tasks = ref<Task[]>([])
const currentTask = ref<Task | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

export function useTask() {
  async function submit(projectId: string, prompt: string) {
    loading.value = true
    error.value = null
    try {
      const task = await createTask(projectId, prompt)
      currentTask.value = task
      tasks.value.unshift(task)
      return task
    } catch (e: any) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  async function loadTasks(projectId?: string) {
    loading.value = true
    try {
      tasks.value = await listTasks(projectId)
    } finally {
      loading.value = false
    }
  }

  async function refresh(taskId: string) {
    currentTask.value = await getTask(taskId)
  }

  async function cancel(taskId: string) {
    await cancelTask(taskId)
    await refresh(taskId)
  }

  return { tasks, currentTask, loading, error, submit, loadTasks, refresh, cancel }
}
