import { useEffect, useState, useCallback } from 'react'
import { getBoard, createTask, updateTask, deleteTask, moveTask } from './api'
import TaskCard from './TaskCard.jsx'
import NewTaskForm from './NewTaskForm.jsx'

const BOARD_ID = 1

export default function App() {
  const [board, setBoard] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [priorityFilter, setPriorityFilter] = useState('')

  const loadBoard = useCallback(async (priority) => {
    setLoading(true)
    setError(null)
    try {
      const data = await getBoard(BOARD_ID, priority || undefined)
      setBoard(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadBoard(priorityFilter)
  }, [priorityFilter, loadBoard])

  async function handleCreate(columnId, payload) {
    await createTask({ ...payload, column_id: columnId })
    await loadBoard(priorityFilter)
  }

  async function handleEdit(taskId, payload) {
    await updateTask(taskId, payload)
    await loadBoard(priorityFilter)
  }

  async function handleDelete(taskId) {
    try {
      await deleteTask(taskId)
      await loadBoard(priorityFilter)
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleMove(taskId, columnId) {
    try {
      await moveTask(taskId, columnId)
      await loadBoard(priorityFilter)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>{board?.name || 'TaskFlow'}</h1>
          <p className="subtitle">A lightweight task board for small teams</p>
        </div>
        <div className="filter-bar">
          <label htmlFor="priority-filter">Filter by priority</label>
          <select
            id="priority-filter"
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="">All</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
      </header>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button onClick={() => loadBoard(priorityFilter)}>Retry</button>
        </div>
      )}

      {loading && !board && <p className="loading">Loading board…</p>}

      {board && (
        <div className="board">
          {board.columns.map((col) => (
            <div className="column" key={col.id}>
              <div className="column-header">
                <h2>{col.name}</h2>
                <span className="task-count">{col.tasks.length}</span>
              </div>

              <div className="task-list">
                {col.tasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    columns={board.columns}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                    onMove={handleMove}
                  />
                ))}
                {col.tasks.length === 0 && (
                  <p className="empty-hint">No tasks here yet.</p>
                )}
              </div>

              <NewTaskForm onCreate={(payload) => handleCreate(col.id, payload)} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
