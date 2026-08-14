import { useState } from 'react'

const PRIORITY_STYLES = {
  High: { bg: '#FDECEA', fg: '#B3261E', dot: '#E4483A' },
  Medium: { bg: '#FFF3E0', fg: '#9A5B00', dot: '#F2A93B' },
  Low: { bg: '#EAF3EC', fg: '#276749', dot: '#4C9A6E' },
}

export default function TaskCard({ task, columns, onEdit, onDelete, onMove }) {
  const [editing, setEditing] = useState(false)
  const [title, setTitle] = useState(task.title)
  const [description, setDescription] = useState(task.description || '')
  const [priority, setPriority] = useState(task.priority)
  const [saving, setSaving] = useState(false)
  const [localError, setLocalError] = useState(null)

  const style = PRIORITY_STYLES[task.priority] || PRIORITY_STYLES.Medium

  async function handleSave() {
    if (!title.trim()) {
      setLocalError('Title cannot be empty.')
      return
    }
    setSaving(true)
    setLocalError(null)
    try {
      await onEdit(task.id, { title: title.trim(), description, priority })
      setEditing(false)
    } catch (err) {
      setLocalError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (editing) {
    return (
      <div className="task-card task-card--editing">
        <input
          className="task-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Task title"
        />
        <textarea
          className="task-textarea"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Description (optional)"
        />
        <select
          className="task-select"
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
        >
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
        </select>
        {localError && <p className="field-error">{localError}</p>}
        <div className="task-card-actions">
          <button className="btn btn--primary" disabled={saving} onClick={handleSave}>
            {saving ? 'Saving…' : 'Save'}
          </button>
          <button className="btn" onClick={() => setEditing(false)} disabled={saving}>
            Cancel
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="task-card">
      <div className="task-card-top">
        <span
          className="priority-pill"
          style={{ background: style.bg, color: style.fg }}
        >
          <span className="priority-dot" style={{ background: style.dot }} />
          {task.priority}
        </span>
      </div>
      <h4 className="task-title">{task.title}</h4>
      {task.description && <p className="task-desc">{task.description}</p>}

      <div className="task-card-footer">
        <select
          className="move-select"
          value={task.column_id}
          onChange={(e) => onMove(task.id, Number(e.target.value))}
          aria-label="Move task to column"
        >
          {columns.map((c) => (
            <option key={c.id} value={c.id}>
              {c.id === task.column_id ? `📍 ${c.name}` : `Move to ${c.name}`}
            </option>
          ))}
        </select>
        <div className="task-card-actions">
          <button className="icon-btn" onClick={() => setEditing(true)} title="Edit">
            ✎
          </button>
          <button className="icon-btn icon-btn--danger" onClick={() => onDelete(task.id)} title="Delete">
            ✕
          </button>
        </div>
      </div>
    </div>
  )
}
