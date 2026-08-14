const BASE_URL = 'http://127.0.0.1:5000/api'

async function handleResponse(res) {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.error || 'Something went wrong. Please try again.')
  }
  return data
}

export async function getBoard(boardId, priority) {
  const url = priority
    ? `${BASE_URL}/boards/${boardId}?priority=${encodeURIComponent(priority)}`
    : `${BASE_URL}/boards/${boardId}`
  const res = await fetch(url)
  return handleResponse(res)
}

export async function createTask(payload) {
  const res = await fetch(`${BASE_URL}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return handleResponse(res)
}

export async function updateTask(taskId, payload) {
  const res = await fetch(`${BASE_URL}/tasks/${taskId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return handleResponse(res)
}

export async function deleteTask(taskId) {
  const res = await fetch(`${BASE_URL}/tasks/${taskId}`, { method: 'DELETE' })
  return handleResponse(res)
}

export async function moveTask(taskId, columnId) {
  const res = await fetch(`${BASE_URL}/tasks/${taskId}/move`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ column_id: columnId }),
  })
  return handleResponse(res)
}
