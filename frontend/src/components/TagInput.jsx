import { useRef } from 'react'

export default function TagInput({ value = [], onChange, placeholder = 'Type and press Enter…', color = 'blue' }) {
  const inputRef = useRef(null)

  function add(raw) {
    const tag = raw.trim().replace(/,$/, '').trim()
    if (tag && !value.includes(tag)) onChange([...value, tag])
  }

  function remove(tag) {
    onChange(value.filter(t => t !== tag))
  }

  function onKeyDown(e) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      add(e.target.value)
      e.target.value = ''
    } else if (e.key === 'Backspace' && !e.target.value && value.length > 0) {
      remove(value[value.length - 1])
    }
  }

  function onBlur(e) {
    if (e.target.value.trim()) {
      add(e.target.value)
      e.target.value = ''
    }
  }

  return (
    <div
      className="tag-input-wrap"
      onClick={() => inputRef.current?.focus()}
    >
      {value.map(tag => (
        <span key={tag} className={`tag-chip ${color}`}>
          {tag}
          <button type="button" onClick={e => { e.stopPropagation(); remove(tag) }}>×</button>
        </span>
      ))}
      <input
        ref={inputRef}
        className="tag-input-inner"
        onKeyDown={onKeyDown}
        onBlur={onBlur}
        placeholder={value.length === 0 ? placeholder : '+ add more'}
      />
    </div>
  )
}
