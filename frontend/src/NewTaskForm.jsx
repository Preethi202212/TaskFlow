import { useState } from 'react'

export default function NewTaskForm({ onCreate }) {
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState('Medium')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!title.trim()) {
      setError('Title cannot be empty.')
      return
    }
    setSaving(true)
    setError(null)
    try {
      await onCreate({ title: title.trim(), description, priority })
      setTitle('')
      setDescription('')
      setPriority('Medium')
      setOpen(false)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (!open) {
    return (
      <button className="add-task-btn" onClick={() => setOpen(true)}>
        + Add task
      </button>
    )
  }

  return (
    <form className="new-task-form" onSubmit={handleSubmit}>
      <input
        className="task-input"
        autoFocus
        placeholder="Task title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <textarea
        className="task-textarea"
        placeholder="Description (optional)"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
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
      {error && <p className="field-error">{error}</p>}
      <div className="task-card-actions">
        <button className="btn btn--primary" type="submit" disabled={saving}>
          {saving ? 'Adding…' : 'Add'}
        </button>
        <button className="btn" type="button" onClick={() => setOpen(false)} disabled={saving}>
          Cancel
        </button>
      </div>
    </form>
  )
}
