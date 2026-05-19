import { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'

type Status = 'idle' | 'dragging' | 'loading' | 'error'

export default function UploadPage() {
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)

  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [status, setStatus] = useState<Status>('idle')
  const [errorMsg, setErrorMsg] = useState<string>('')

  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith('image/')) {
      setErrorMsg('Пожалуйста, загрузите изображение (PNG, JPG и т.д.)')
      setStatus('error')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      setErrorMsg('Файл слишком большой. Максимум — 10 МБ.')
      setStatus('error')
      return
    }
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setStatus('idle')
    setErrorMsg('')
  }, [])

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setStatus('dragging')
  }

  const onDragLeave = () => {
    setStatus('idle')
  }

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const f = e.dataTransfer.files[0]
    if (f) handleFile(f)
    else setStatus('idle')
  }

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) handleFile(f)
  }

  const handleRemove = () => {
    setFile(null)
    setPreview(null)
    setStatus('idle')
    setErrorMsg('')
    if (inputRef.current) inputRef.current.value = ''
  }

  const handleSubmit = async () => {
    if (!file) return
    setStatus('loading')
    setErrorMsg('')

    const formData = new FormData()
    formData.append('image', file)

    try {
      const res = await fetch('/classify', {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        throw new Error(`Ошибка сервера: ${res.status}`)
      }

      const data = await res.json()
      // Pass result to ResultPage via router state
      navigate('/result', { state: { result: data } })
    } catch (err) {
      setStatus('error')
      setErrorMsg(err instanceof Error ? err.message : 'Что-то пошло не так. Попробуйте ещё раз.')
    }
  }

  const isDragging = status === 'dragging'
  const isLoading = status === 'loading'

  return (
    <div className="max-w-lg mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-2">Загрузка фото</h1>
      <p className="text-gray-500 mb-8">Загрузите фото блюда для анализа состава.</p>

      {/* Drop zone */}
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => !file && inputRef.current?.click()}
        className={`
          relative border-2 border-dashed rounded-xl transition-colors duration-200
          ${file ? 'border-teal-400 bg-white cursor-default' : 'cursor-pointer'}
          ${isDragging ? 'border-teal-500 bg-teal-100 scale-[1.01]' : ''}
          ${!file && !isDragging ? 'border-teal-500 bg-teal-50 hover:bg-teal-100' : ''}
        `}
      >
        {preview ? (
          <div className="relative">
            <img
              src={preview}
              alt="Предпросмотр"
              className="w-full max-h-72 object-contain rounded-xl p-2"
            />
            {/* Remove button */}
            <button
              onClick={(e) => { e.stopPropagation(); handleRemove() }}
              className="absolute top-3 right-3 w-7 h-7 bg-white border border-gray-200 rounded-full shadow text-gray-500 hover:text-red-500 hover:border-red-300 transition-colors flex items-center justify-center text-sm"
              title="Удалить"
            >
              ✕
            </button>
            {/* File name */}
            <div className="px-4 pb-3 text-xs text-gray-400 truncate">{file?.name}</div>
          </div>
        ) : (
          <div className="p-16 flex flex-col items-center gap-3">
            <span className="text-5xl">{isDragging ? '📂' : '📷'}</span>
            <span className="font-medium text-gray-700">
              {isDragging ? 'Отпустите для загрузки' : 'Перетащите фото сюда'}
            </span>
            <span className="text-sm text-gray-400">или нажмите для выбора · PNG, JPG · до 10 МБ</span>
          </div>
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={onInputChange}
      />

      {/* Error message */}
      {status === 'error' && errorMsg && (
        <p className="mt-3 text-sm text-red-500">{errorMsg}</p>
      )}

      {/* Action buttons */}
      <div className="flex gap-3 mt-6">
        <button
          onClick={() => inputRef.current?.click()}
          disabled={isLoading}
          className="flex-1 py-3 border border-gray-300 rounded-lg font-medium text-gray-600 hover:border-teal-500 hover:text-teal-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Выбрать файл
        </button>
        <button
          onClick={handleSubmit}
          disabled={!file || isLoading}
          className="flex-1 py-3 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {isLoading ? (
            <>
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Анализ...
            </>
          ) : (
            'Анализировать'
          )}
        </button>
      </div>
    </div>
  )
}
