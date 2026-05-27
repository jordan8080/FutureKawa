import { clsx } from 'clsx'

const VARIANTS = {
  primary: 'bg-amber-500 hover:bg-amber-400 text-gray-950 font-semibold',
  secondary: 'bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700',
  ghost: 'hover:bg-gray-800 text-gray-400 hover:text-white',
  danger: 'bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20',
}

const SIZES = {
  sm: 'text-xs px-3 py-1.5 rounded-lg',
  md: 'text-sm px-4 py-2 rounded-lg',
  lg: 'text-base px-5 py-2.5 rounded-xl',
}

export function Button({ children, variant = 'secondary', size = 'md', className, disabled, onClick, type = 'button', icon }) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={clsx(
        'inline-flex items-center gap-2 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-amber-500/40',
        VARIANTS[variant],
        SIZES[size],
        disabled && 'opacity-50 cursor-not-allowed pointer-events-none',
        className
      )}
    >
      {icon && <span className="flex-shrink-0">{icon}</span>}
      {children}
    </button>
  )
}
