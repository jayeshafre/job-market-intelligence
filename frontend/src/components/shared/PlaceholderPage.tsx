// PlaceholderPage.tsx
//
// Temporary stand-in for pages not yet built.
// Shows the page name and a "coming in Phase X" note.
// Replace with real page components phase by phase.

interface PlaceholderPageProps {
  title: string
  phase?: string
  description?: string
}

export default function PlaceholderPage({
  title,
  phase = 'Next Phase',
  description = 'This module is under construction.',
}: PlaceholderPageProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full min-h-[400px] gap-4 text-center page-enter">
      {/* Icon box */}
      <div
        className="w-14 h-14 rounded-xl flex items-center justify-center"
        style={{
          background: 'rgba(34,211,238,0.08)',
          border: '1px solid rgba(34,211,238,0.2)',
        }}
      >
        <span className="font-mono text-accent-DEFAULT text-lg font-medium">
          {title.charAt(0)}
        </span>
      </div>

      {/* Title */}
      <div>
        <p className="font-mono text-[11px] uppercase tracking-widest text-text-muted mb-1">
          {phase}
        </p>
        <h1 className="text-xl font-semibold text-text-primary tracking-tight">
          {title}
        </h1>
        <p className="text-[13px] text-text-secondary mt-1.5 max-w-xs">
          {description}
        </p>
      </div>

      {/* Status pill */}
      <span
        className="font-mono text-[10px] uppercase tracking-widest px-3 py-1.5 rounded-full"
        style={{
          background: 'rgba(34,211,238,0.08)',
          border: '1px solid rgba(34,211,238,0.2)',
          color: '#22D3EE',
        }}
      >
        Coming Soon
      </span>
    </div>
  )
}