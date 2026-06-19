export function LoadingSpinner({ size = 'md', center = false }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-7 h-7', lg: 'w-10 h-10' }
  const spinner = (
    <svg className={`${sizes[size]} animate-spin text-amber-500`} fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  )
  if (center) return <div className="flex justify-center items-center py-16">{spinner}</div>
  return spinner
}

export function PageLoader() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24">
      <LoadingSpinner size="lg" />
      <p className="text-sm text-gray-500">Chargement…</p>
    </div>
  )
}

export function SkeletonLine({ className = '' }) {
  return <div className={`bg-gray-800 animate-pulse rounded ${className}`} />
}
