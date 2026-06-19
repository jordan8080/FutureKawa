import { clsx } from 'clsx'

export function Card({ children, className, onClick, hover = false }) {
  return (
    <div
      className={clsx(
        'bg-gray-900 border border-gray-800 rounded-xl',
        hover && 'hover:border-gray-700 hover:bg-gray-800/80 transition-all duration-200 cursor-pointer',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className }) {
  return <div className={clsx('px-5 py-4 border-b border-gray-800', className)}>{children}</div>
}

export function CardBody({ children, className }) {
  return <div className={clsx('px-5 py-4', className)}>{children}</div>
}
