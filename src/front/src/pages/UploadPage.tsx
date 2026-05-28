import { useRef, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useToast } from '../components/Toast'

type Status = 'idle' | 'dragging' | 'loading' | 'error'

export default function UploadPage() {
  const [file, setFile]         = useState<File | null>(null)
  const [preview, setPreview]   = useState<string | null>(null)
  const [status, setStatus]     = useState<Status>('idle')
  const [errorMsg, setErrorMsg] = useState<string>('')
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  const { toast } = useToast()

  const handleFile = useCallback((f: File) => {
    if (!f.type.startsWith('image/')) {
      setErrorMsg('Поддерживаются только изображения (PNG, JPG, WEBP)')
      setStatus('error')
      toast.error('Поддерживаются только изображения (PNG, JPG, WEBP)')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      setErrorMsg('Файл слишком большой. Максимум — 10 МБ')
      setStatus('error')
      toast.error('Файл слишком большой. Максимум — 10 МБ')
      return
    }
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setStatus('idle')
    setErrorMsg('')
    toast.info('Фото загружено — нажми «Анализировать»')
  }, [toast])

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) handleFile(f)
  }

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setStatus('idle')
    const f = e.dataTransfer.files?.[0]
    if (f) handleFile(f)
  }, [handleFile])

  const onDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setStatus('dragging')
  }

  const onDragLeave = () => setStatus('idle')

  const reset = () => {
    setFile(null)
    setPreview(null)
    setStatus('idle')
    setErrorMsg('')
    if (inputRef.current) inputRef.current.value = ''
  }

  const handleAnalyze = async () => {
    if (!file) return
    setStatus('loading')
    setErrorMsg('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/api/classify', {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `Ошибка сервера: ${res.status}`)
      }
      const data = await res.json()
      toast.success('Продукт успешно распознан!')
      navigate('/result', { state: { result: data } })
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Что-то пошло не так. Попробуйте ещё раз.'
      setStatus('error')
      setErrorMsg(msg)
      toast.error(msg)
    }
  }

  const isDragging = status === 'dragging'
  const isLoading  = status === 'loading'

  return (
    <div className="max-w-lg mx-auto py-10 px-4">
      <h1 className="text-2xl font-bold mb-2 dark:text-gray-50">Загрузка фото</h1>
      <p className="text-gray-500 dark:text-gray-400 mb-8">Загрузите фото блюда для анализа состава.</p>

      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onClick={() => !preview && inputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl transition-colors duration-200 overflow-hidden
          ${isDragging
            ? 'border-teal-400 bg-teal-100 dark:bg-teal-900/30'
            : preview
              ? 'border-teal-500 bg-white dark:bg-gray-900 cursor-default'
              : 'border-teal-500 bg-teal-50 dark:bg-teal-900/20 cursor-pointer hover:bg-teal-100 dark:hover:bg-teal-900/30'
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
            <button
              onClick={(e) => { e.stopPropagation(); reset() }}
              className="absolute top-3 right-3 w-7 h-7 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full shadow text-gray-500 hover:text-red-500 hover:border-red-300 transition-colors flex items-center justify-center text-sm"
              title="Удалить"
            >
              ✕
            </button>
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
            <span className="font-medium text-gray-700 dark:text-gray-300">
              {isDragging ? 'Отпустите файл' : 'Перетащите или выберите фото'}
            </span>
            <span className="text-sm text-gray-400 dark:text-gray-500">PNG, JPG, WEBP · до 10 МБ</span>
          </div>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={onInputChange}
      />

      {status === 'error' && errorMsg && (
        <div className="mt-4 px-4 py-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600 dark:text-red-400 text-sm">
          {errorMsg}
        </div>
      )}

      <div className="flex gap-3 mt-6">
        <button
          onClick={preview ? reset : () => inputRef.current?.click()}
          className="flex-1 py-3 border border-gray-300 dark:border-gray-700 dark:text-gray-300 rounded-lg font-medium text-gray-600 hover:border-teal-500 hover:text-teal-600 dark:hover:border-teal-500 dark:hover:text-teal-400 transition-colors disabled:opacity-50"
          disabled={isLoading}
        >
          {preview ? 'Удалить' : 'Выбрать файл'}
        </button>

        <button
          onClick={handleAnalyze}
          disabled={!file || isLoading}
          className={`flex-1 py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2
            ${!file || isLoading
              ? 'bg-teal-300 dark:bg-teal-800 text-white cursor-not-allowed'
              : 'bg-teal-600 text-white hover:bg-teal-700 cursor-pointer'
            }`}
        >
          {isLoading ? (
            <>
              <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Анализируем…
            </>
          ) : (
            'Анализировать'
          )}
        </button>
      </div>
    </div>
  )
}
