<<<<<<< HEAD
import { useRef, useState, useCallback } from 'react'
=======
import { useState, useRef, useCallback } from 'react'
>>>>>>> a48e160 (Add drag-and-drop, image preview and POST /classify)
import { useNavigate } from 'react-router-dom'

type Status = 'idle' | 'dragging' | 'loading' | 'error'

export default function UploadPage() {
<<<<<<< HEAD
  const [file, setFile]       = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [status, setStatus]   = useState<Status>('idle')
  const [errorMsg, setErrorMsg] = useState<string>('')
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  const handleFile = (f: File) => {
    if (!f.type.startsWith('image/')) {
      setErrorMsg('Поддерживаются только изображения (PNG, JPG, WEBP)')
=======
  const navigate = useNavigate()
  const inputRef = useRef<HTMLInputElement>(null)

  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [status, setStatus] = useState<Status>('idle')
  const [errorMsg, setErrorMsg] = useState<string>('')

  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith('image/')) {
      setErrorMsg('Пожалуйста, загрузите изображение (PNG, JPG и т.д.)')
>>>>>>> a48e160 (Add drag-and-drop, image preview and POST /classify)
      setStatus('error')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
<<<<<<< HEAD
      setErrorMsg('Файл слишком большой. Максимум — 10 МБ')
=======
      setErrorMsg('Файл слишком большой. Максимум — 10 МБ.')
>>>>>>> a48e160 (Add drag-and-drop, image preview and POST /classify)
      setStatus('error')
      return
    }
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setStatus('idle')
    setErrorMsg('')
<<<<<<< HEAD
=======
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
>>>>>>> a48e160 (Add drag-and-drop, image preview and POST /classify)
  }

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) handleFile(f)
  }

<<<<<<< HEAD
  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setStatus('idle')
    const f = e.dataTransfer.files?.[0]
    if (f) handleFile(f)
  }, [])

  const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setStatus('dragging')
  }

  const onDragLeave = () => setStatus('idle')

  const handleAnalyze = async () => {
=======
  const handleRemove = () => {
    setFile(null)
    setPreview(null)
    setStatus('idle')
    setErrorMsg('')
    if (inputRef.current) inputRef.current.value = ''
  }

  const handleSubmit = async () => {
>>>>>>> a48e160 (Add drag-and-drop, image preview and POST /classify)
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
<<<<<<< HEAD
        const text = await res.text()
        throw new Error(text || `Ошибка сервера: ${res.status}`)
      }

      const data = await res.json()
      // Navigate to result page, passing the response in location state
      navigate('/result', { state: { result: data } })
    } catch (err) {
      setStatus('error')
      setErrorMsg(err instanceof Error ? err.message : 'Неизвестная ошибка')
    }
  }

  const reset = () => {
    setFile(null)
    setPreview(null)
    setStatus('idle')
    setErrorMsg('')
    if (inputRef.current) inputRef.current.value = ''
  }

  const isDragging = status === 'dragging'
  const isLoading  = status === 'loading'
=======
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
>>>>>>> a48e160 (Add drag-and-drop, image preview and POST /classify)

  return (
    <div className="max-w-lg mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-2">Загрузка фото</h1>
      <p className="text-gray-500 mb-8">Загрузите фото блюда для анализа состава.</p>

      {/* Drop zone */}
      <div
<<<<<<< HEAD
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => !preview && inputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl transition-colors duration-200 overflow-hidden
          ${isDragging
            ? 'border-teal-400 bg-teal-100'
            : preview
              ? 'border-teal-500 bg-white cursor-default'
              : 'border-teal-500 bg-teal-50 cursor-pointer hover:bg-teal-100'
          }
          ${preview ? 'p-0' : 'p-16'}
        `}
      >
        {preview ? (
          <>
            <img
              src={preview}
              alt="Предпросмотр"
              className="w-full max-h-72 object-cover rounded-xl"
            />
            {/* Overlay with filename */}
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 to-transparent px-4 py-3 rounded-b-xl">
              <p className="text-white text-sm font-medium truncate">{file?.name}</p>
              <p className="text-white/70 text-xs">
                {file ? (file.size / 1024 / 1024).toFixed(2) + ' МБ' : ''}
              </p>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center gap-3 select-none">
            <span className="text-5xl">{isDragging ? '📂' : '📷'}</span>
            <span className="font-medium text-gray-700">
              {isDragging ? 'Отпустите файл' : 'Перетащите или выберите фото'}
            </span>
            <span className="text-sm text-gray-400">PNG, JPG, WEBP · до 10 МБ</span>
=======
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
>>>>>>> a48e160 (Add drag-and-drop, image preview and POST /classify)
          </div>
        )}
      </div>

<<<<<<< HEAD
=======
      {/* Hidden file input */}
>>>>>>> a48e160 (Add drag-and-drop, image preview and POST /classify)
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={onInputChange}
      />

      {/* Error message */}
      {status === 'error' && errorMsg && (
<<<<<<< HEAD
        <div className="mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {errorMsg}
        </div>
=======
        <p className="mt-3 text-sm text-red-500">{errorMsg}</p>
>>>>>>> a48e160 (Add drag-and-drop, image preview and POST /classify)
      )}

      {/* Action buttons */}
      <div className="flex gap-3 mt-6">
        <button
<<<<<<< HEAD
          onClick={preview ? reset : () => inputRef.current?.click()}
          className="flex-1 py-3 border border-gray-300 rounded-lg font-medium text-gray-600 hover:border-teal-500 hover:text-teal-600 transition-colors"
          disabled={isLoading}
        >
          {preview ? 'Удалить' : 'Выбрать файл'}
        </button>

        <button
          onClick={handleAnalyze}
          disabled={!file || isLoading}
          className={`flex-1 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2
            ${!file || isLoading
              ? 'bg-teal-300 text-white cursor-not-allowed'
              : 'bg-teal-600 text-white hover:bg-teal-700 cursor-pointer'
            }`}
        >
          {isLoading ? (
            <>
              <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Анализируем…
=======
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
>>>>>>> a48e160 (Add drag-and-drop, image preview and POST /classify)
            </>
          ) : (
            'Анализировать'
          )}
        </button>
      </div>
    </div>
  )
}
