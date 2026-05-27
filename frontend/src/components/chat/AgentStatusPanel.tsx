import type { AgentOutput } from '@/types/ai'
import { useState } from 'react'
import { CheckCircle, XCircle, ChevronDown, ChevronUp, Cpu } from 'lucide-react'

interface Props {
  agentOutputs:  AgentOutput[]
  executionPlan: string[]
  agentsRun:     number
  agentsFailed:  number
}

export default function AgentStatusPanel({ agentOutputs, executionPlan, agentsRun, agentsFailed }: Props) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="mt-3 rounded-xl overflow-hidden"
      style={{ background: '#161B22', border: '1px solid #21262D' }}>

      {/* Header */}
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center justify-between px-3 py-2.5 hover:bg-base-700 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Cpu size={12} className="text-info" />
          <span className="font-mono text-[10px] text-text-secondary uppercase tracking-wider">
            Multi-Agent System
          </span>
          <span className="font-mono text-[9px] px-1.5 py-0.5 rounded"
            style={{ background: 'rgba(129,140,248,0.1)', color: '#818CF8', border: '1px solid rgba(129,140,248,0.2)' }}>
            {agentsRun} agents ran
          </span>
          {agentsFailed > 0 && (
            <span className="font-mono text-[9px] text-danger">{agentsFailed} failed</span>
          )}
        </div>
        {expanded ? <ChevronUp size={12} className="text-text-muted" /> : <ChevronDown size={12} className="text-text-muted" />}
      </button>

      {/* Expanded detail */}
      {expanded && (
        <div className="px-3 pb-3 space-y-2 border-t border-border">
          {/* Execution plan */}
          <div className="mt-2">
            <p className="font-mono text-[9px] text-text-muted uppercase tracking-wider mb-1.5">Execution Plan</p>
            <div className="space-y-0.5">
              {executionPlan.map((step, i) => (
                <p key={i} className="font-mono text-[10px] text-text-secondary">
                  <span className="text-text-muted mr-2">{i + 1}.</span>{step}
                </p>
              ))}
            </div>
          </div>

          {/* Agent outputs */}
          <div className="mt-2">
            <p className="font-mono text-[9px] text-text-muted uppercase tracking-wider mb-1.5">Agent Reports</p>
            <div className="space-y-2">
              {agentOutputs.map((agent, i) => (
                <div key={i} className="rounded-lg px-2.5 py-2"
                  style={{ background: '#1C2333', border: `1px solid ${agent.success ? '#21262D' : 'rgba(248,113,113,0.2)'}` }}>
                  <div className="flex items-center gap-2 mb-1">
                    {agent.success
                      ? <CheckCircle size={11} className="text-success flex-shrink-0" />
                      : <XCircle    size={11} className="text-danger  flex-shrink-0" />}
                    <span className="font-mono text-[10px] font-medium text-text-primary">{agent.agent_name}</span>
                    <span className="font-mono text-[9px] text-text-muted">{agent.domain}</span>
                  </div>
                  {agent.success
                    ? agent.insights.map((ins, j) => (
                        <p key={j} className="text-[11px] text-text-secondary leading-relaxed pl-4">
                          · {ins}
                        </p>
                      ))
                    : <p className="text-[11px] text-danger pl-4">{agent.error}</p>
                  }
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}