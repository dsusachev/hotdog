// Skeleton.tsx
// Набор skeleton-заглушек, повторяющих форму реальных блоков.
//
// Экспорты:
//   <Skeleton />               — базовая мерцающая полоска (любой размер через className)
//   <SkeletonCard />           — карточка результата (ResultPage)
//   <SkeletonSearchResult />   — строка результата поиска (SearchPage)
//   <SkeletonHistoryItem />    — строка истории (HistoryPage)
//   <SkeletonUploadResult />   — весь блок ResultPage во время загрузки
//
// Пример:
//   import { SkeletonCard } from './Skeleton'
//   {isLoading ? <SkeletonCard /> : <RealCard ... />}

// ─── Base ─────────────────────────────────────────────────────────────────────

interface SkeletonProps {
  className?: string
}

export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div
      className={`bg-gray-200 rounded animate-pulse ${className}`}
      aria-hidden="true"
    />
  )
}

// ─── Card (ResultPage) ────────────────────────────────────────────────────────

export function SkeletonCard() {
  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-6 mb-6">
      {/* icon placeholder */}
      <Skeleton className="w-12 h-12 rounded-full mx-auto mb-4" />

      {/* title */}
      <Skeleton className="h-6 w-2/3 mx-auto mb-5 rounded-lg" />

      {/* two rows: label + value */}
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <Skeleton className="h-4 w-1/3 rounded" />
          <Skeleton className="h-4 w-1/4 rounded" />
        </div>
        <div className="flex justify-between items-center">
          <Skeleton className="h-4 w-2/5 rounded" />
          <Skeleton className="h-4 w-1/5 rounded" />
        </div>
      </div>
    </div>
  )
}

// ─── Search result row ────────────────────────────────────────────────────────

export function SkeletonSearchResult() {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 flex items-center gap-4">
      <Skeleton className="w-10 h-10 rounded-lg flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-1/2 rounded" />
        <Skeleton className="h-3 w-3/4 rounded" />
      </div>
      <Skeleton className="w-14 h-6 rounded-full flex-shrink-0" />
    </div>
  )
}

// ─── History item row ─────────────────────────────────────────────────────────

export function SkeletonHistoryItem() {
  return (
    <div className="flex items-center gap-3 py-3 border-b border-gray-100 last:border-0">
      {/* thumb */}
      <Skeleton className="w-12 h-12 rounded-lg flex-shrink-0" />

      <div className="flex-1 space-y-2 min-w-0">
        <Skeleton className="h-4 w-1/3 rounded" />
        <Skeleton className="h-3 w-1/2 rounded" />
      </div>

      {/* date badge */}
      <Skeleton className="w-16 h-4 rounded flex-shrink-0" />
    </div>
  )
}

// ─── Full upload result (ResultPage while /classify is loading) ───────────────

export function SkeletonUploadResult() {
  return (
    <div className="max-w-md mx-auto py-10 px-4">
      {/* back link */}
      <Skeleton className="h-4 w-16 mb-6 rounded" />

      <SkeletonCard />

      {/* nearby block */}
      <div className="bg-white border border-gray-200 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <Skeleton className="h-5 w-24 rounded" />
          <Skeleton className="h-4 w-20 rounded" />
        </div>

        <div className="space-y-1">
          {[1, 2, 3].map(i => (
            <div key={i} className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-0">
              <Skeleton className="w-7 h-7 rounded-full flex-shrink-0 mt-0.5" />
              <div className="flex-1 space-y-1.5">
                <Skeleton className="h-4 w-2/3 rounded" />
                <Skeleton className="h-3 w-1/2 rounded" />
              </div>
              <Skeleton className="w-10 h-3 rounded flex-shrink-0 mt-1" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ─── Generic page skeleton (for any page that loads data) ────────────────────

export function SkeletonPage({ rows = 4 }: { rows?: number }) {
  return (
    <div className="max-w-2xl mx-auto py-10 px-4 space-y-4">
      <Skeleton className="h-8 w-1/3 rounded-lg mb-8" />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="bg-white border border-gray-200 rounded-xl p-4 space-y-2">
          <Skeleton className="h-4 w-3/4 rounded" />
          <Skeleton className="h-3 w-1/2 rounded" />
        </div>
      ))}
    </div>
  )
}
