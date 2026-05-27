// AI typing indicator — three animated dots
export default function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 mb-4">
      {/* Avatar */}
      <div className="w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
        style={{ background: 'rgba(34,211,238,0.1)', border: '1px solid rgba(34,211,238,0.25)' }}>
        <span className="font-mono text-[10px] text-accent-DEFAULT font-bold">AI</span>
      </div>
      {/* Bubble */}
      <div className="px-4 py-3 rounded-2xl rounded-tl-sm"
        style={{ background: '#1C2333', border: '1px solid #21262D' }}>
        <div className="flex items-center gap-1.5 h-4">
          {[0, 1, 2].map(i => (
            <div
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-accent-DEFAULT"
              style={{ animation: `typing-bounce 1.2s ease-in-out ${i * 0.2}s infinite` }}
            />
          ))}
        </div>
      </div>
      <style>{`
        @keyframes typing-bounce {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-4px); opacity: 1; }
        }
      `}</style>
    </div>
  )
}