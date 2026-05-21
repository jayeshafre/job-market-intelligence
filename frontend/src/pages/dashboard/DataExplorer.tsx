import { useState, useMemo } from 'react'
import { Search, Filter, ChevronUp, ChevronDown } from 'lucide-react'
import PageHeader from '@/components/shared/PageHeader'
import SectionHeader from '@/components/shared/SectionHeader'
import { useWorkforce } from '@/hooks/useWorkforce'
import { useSalary } from '@/hooks/useSalary'
import { useSkills } from '@/hooks/useSkills'
import { useAiImpact } from '@/hooks/useAiImpact'
import KpiCard, { fmtNumber } from '@/components/dashboard/KpiCard'
import { Database, Table } from 'lucide-react'

// ─────────────────────────────────────────
// DataExplorer
//
// Unified searchable, filterable, sortable
// table view across all four datasets.
// All data from real API endpoints.
//
// Dataset tabs:
//   Workforce  → /api/v1/workforce/by-country
//   Salary     → /api/v1/salary/by-role
//   Skills     → /api/v1/skills/top-growing
//   AI Impact  → /api/v1/ai-impact/disruption-scores
// ─────────────────────────────────────────

type DatasetTab = 'workforce' | 'salary' | 'skills' | 'ai-impact'
type SortDir = 'asc' | 'desc'

interface SortState { key: string; dir: SortDir }

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <ChevronUp size={10} className="text-text-muted opacity-40" />
  return dir === 'asc'
    ? <ChevronUp size={10} className="text-accent-DEFAULT" />
    : <ChevronDown size={10} className="text-accent-DEFAULT" />
}

function ColHeader({
  label, sortKey, sort, onSort, className = '',
}: {
  label: string; sortKey: string
  sort: SortState; onSort: (k: string) => void; className?: string
}) {
  return (
    <button
      onClick={() => onSort(sortKey)}
      className={`flex items-center gap-1 font-mono text-[10px] text-text-muted uppercase tracking-wider
                  hover:text-text-secondary transition-colors ${className}`}
    >
      {label}
      <SortIcon active={sort.key === sortKey} dir={sort.dir} />
    </button>
  )
}

function useSort<T>(data: T[], sort: SortState): T[] {
  return useMemo(() => {
    if (!sort.key) return data
    return [...data].sort((a: any, b: any) => {
      const av = a[sort.key] ?? ''
      const bv = b[sort.key] ?? ''
      const cmp = typeof av === 'number' ? av - bv : String(av).localeCompare(String(bv))
      return sort.dir === 'asc' ? cmp : -cmp
    })
  }, [data, sort])
}

export default function DataExplorer() {
  const workforce = useWorkforce()
  const salary    = useSalary()
  const skills    = useSkills()
  const aiImpact  = useAiImpact()

  const [tab, setTab]       = useState<DatasetTab>('workforce')
  const [search, setSearch] = useState('')
  const [sort, setSort]     = useState<SortState>({ key: '', dir: 'desc' })

  const isLoading = {
    workforce: workforce.status === 'idle' || workforce.status === 'loading',
    salary:    salary.status    === 'idle' || salary.status    === 'loading',
    skills:    skills.status    === 'idle' || skills.status    === 'loading',
    'ai-impact': aiImpact.status === 'idle' || aiImpact.status === 'loading',
  }[tab]

  function handleSort(key: string) {
    setSort(prev =>
      prev.key === key
        ? { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' }
        : { key, dir: 'desc' }
    )
  }

  function handleTabChange(t: DatasetTab) {
    setTab(t)
    setSearch('')
    setSort({ key: '', dir: 'desc' })
  }

  // ── Dataset: Workforce countries ─────────
  const workforceRaw   = workforce.data?.byCountry ?? []
  const workforceSorted = useSort(workforceRaw, sort)
  const workforceFiltered = useMemo(() =>
    workforceSorted.filter(r =>
      r.country_name.toLowerCase().includes(search.toLowerCase()) ||
      r.region.toLowerCase().includes(search.toLowerCase())
    ), [workforceSorted, search])

  // ── Dataset: Salary by role ───────────────
  const salaryRaw     = salary.data?.byRole ?? []
  const salarySorted  = useSort(salaryRaw, sort)
  const salaryFiltered = useMemo(() =>
    salarySorted.filter(r =>
      r.role_name.toLowerCase().includes(search.toLowerCase()) ||
      r.role_category.toLowerCase().includes(search.toLowerCase()) ||
      r.seniority_level.toLowerCase().includes(search.toLowerCase())
    ), [salarySorted, search])

  // ── Dataset: Skills ───────────────────────
  const skillsRaw     = skills.data?.topGrowing ?? []
  const skillsSorted  = useSort(skillsRaw, sort)
  const skillsFiltered = useMemo(() =>
    skillsSorted.filter(r =>
      r.skill_name.toLowerCase().includes(search.toLowerCase()) ||
      r.skill_category.toLowerCase().includes(search.toLowerCase())
    ), [skillsSorted, search])

  // ── Dataset: AI disruption scores ─────────
  const aiRaw     = aiImpact.data?.disruptionScores ?? []
  const aiSorted  = useSort(aiRaw, sort)
  const aiFiltered = useMemo(() =>
    aiSorted.filter(r =>
      r.role_name.toLowerCase().includes(search.toLowerCase()) ||
      r.role_category.toLowerCase().includes(search.toLowerCase())
    ), [aiSorted, search])

  // Total records for KPI
  const totalRecords = {
    workforce: workforceRaw.length,
    salary:    salaryRaw.length,
    skills:    skillsRaw.length,
    'ai-impact': aiRaw.length,
  }

  const TABS: { id: DatasetTab; label: string; endpoint: string }[] = [
    { id: 'workforce',  label: 'Workforce',  endpoint: '/workforce/by-country' },
    { id: 'salary',     label: 'Salary',     endpoint: '/salary/by-role' },
    { id: 'skills',     label: 'Skills',     endpoint: '/skills/top-growing' },
    { id: 'ai-impact',  label: 'AI Impact',  endpoint: '/ai-impact/disruption-scores' },
  ]

  return (
    <div className="space-y-5 page-enter">
      <PageHeader
        crumb="data"
        title="Data Explorer"
        description="Search, sort, and filter across all datasets from live API endpoints"
        isLoading={!!isLoading}
        onRefetch={() => {
          workforce.refetch(); salary.refetch()
          skills.refetch();    aiImpact.refetch()
        }}
      />

      {/* KPI row */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard label="Country Records"    value={fmtNumber(totalRecords.workforce)} delta="/workforce/by-country"      trend="neutral" icon={Database} isLoading={workforce.status === 'loading'} />
        <KpiCard label="Role Records"       value={fmtNumber(totalRecords.salary)}    delta="/salary/by-role"            trend="neutral" icon={Database} isLoading={salary.status    === 'loading'} />
        <KpiCard label="Skill Records"      value={fmtNumber(totalRecords.skills)}    delta="/skills/top-growing"        trend="neutral" icon={Table}   isLoading={skills.status    === 'loading'} />
        <KpiCard label="AI Impact Records"  value={fmtNumber(totalRecords['ai-impact'])} delta="/ai-impact/disruption-scores" trend="neutral" icon={Table} isLoading={aiImpact.status === 'loading'} />
      </div>

      <div className="kpi-card space-y-4">
        {/* Tab bar + search */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          {/* Tabs */}
          <div className="flex gap-1 p-1 rounded-lg bg-base-700 w-fit">
            {TABS.map(t => (
              <button
                key={t.id}
                onClick={() => handleTabChange(t.id)}
                className={`px-3 py-1.5 rounded-md text-[12px] font-medium transition-all duration-150
                  ${tab === t.id
                    ? 'bg-base-800 text-text-primary border border-border'
                    : 'text-text-muted hover:text-text-secondary'
                  }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search records…"
              className="pl-8 pr-3 py-1.5 rounded-lg bg-base-700 border border-border text-[12px]
                         text-text-primary placeholder:text-text-muted outline-none w-52
                         focus:border-accent-border transition-colors font-mono"
            />
          </div>
        </div>

        {/* Endpoint badge */}
        <p className="font-mono text-[10px] text-text-muted">
          Source: <span className="text-accent-DEFAULT">/api/v1{TABS.find(t => t.id === tab)?.endpoint}</span>
          {' · '}{({
            workforce: workforceFiltered.length,
            salary: salaryFiltered.length,
            skills: skillsFiltered.length,
            'ai-impact': aiFiltered.length,
          }[tab])} records
        </p>

        {/* ── Workforce table ── */}
        {tab === 'workforce' && (
          <>
            <div className="grid grid-cols-12 gap-2 px-2 border-b border-border pb-2">
              <ColHeader label="Country"    sortKey="country_name"  sort={sort} onSort={handleSort} className="col-span-4" />
              <ColHeader label="Code"       sortKey="country_code"  sort={sort} onSort={handleSort} className="col-span-1" />
              <ColHeader label="Region"     sortKey="region"        sort={sort} onSort={handleSort} className="col-span-3" />
              <ColHeader label="Postings"   sortKey="total_postings" sort={sort} onSort={handleSort} className="col-span-2 justify-end" />
              <ColHeader label="Avg Salary" sortKey="avg_salary_usd" sort={sort} onSort={handleSort} className="col-span-2 justify-end" />
            </div>
            <div className="space-y-0.5 max-h-96 overflow-y-auto">
              {isLoading ? Array(8).fill(null).map((_, i) => (
                <div key={i} className="h-9 bg-base-700 rounded animate-pulse" />
              )) : workforceFiltered.map(r => (
                <div key={r.country_name} className="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded-md hover:bg-base-700 transition-colors duration-150">
                  <span className="col-span-4 text-[12px] text-text-primary truncate">{r.country_name}</span>
                  <span className="col-span-1 font-mono text-[11px] text-text-muted">{r.country_code}</span>
                  <span className="col-span-3 font-mono text-[11px] text-text-muted truncate">{r.region}</span>
                  <span className="col-span-2 font-mono text-[11px] text-accent-DEFAULT text-right">{fmtNumber(r.total_postings)}</span>
                  <span className="col-span-2 font-mono text-[11px] text-text-secondary text-right">
                    {r.avg_salary_usd ? `$${Math.round(r.avg_salary_usd / 1000)}K` : '—'}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}

        {/* ── Salary table ── */}
        {tab === 'salary' && (
          <>
            <div className="grid grid-cols-12 gap-2 px-2 border-b border-border pb-2">
              <ColHeader label="Role"       sortKey="role_name"      sort={sort} onSort={handleSort} className="col-span-4" />
              <ColHeader label="Category"   sortKey="role_category"  sort={sort} onSort={handleSort} className="col-span-3" />
              <ColHeader label="Level"      sortKey="seniority_level" sort={sort} onSort={handleSort} className="col-span-2" />
              <ColHeader label="Avg Salary" sortKey="avg_salary_usd"  sort={sort} onSort={handleSort} className="col-span-2 justify-end" />
              <ColHeader label="N"          sortKey="data_points"     sort={sort} onSort={handleSort} className="col-span-1 justify-end" />
            </div>
            <div className="space-y-0.5 max-h-96 overflow-y-auto">
              {isLoading ? Array(8).fill(null).map((_, i) => (
                <div key={i} className="h-9 bg-base-700 rounded animate-pulse" />
              )) : salaryFiltered.map(r => (
                <div key={`${r.role_name}-${r.seniority_level}`} className="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded-md hover:bg-base-700 transition-colors duration-150">
                  <span className="col-span-4 text-[12px] text-text-primary truncate">{r.role_name}</span>
                  <span className="col-span-3 font-mono text-[11px] text-text-muted truncate">{r.role_category}</span>
                  <span className="col-span-2 font-mono text-[11px] text-text-muted truncate">{r.seniority_level}</span>
                  <span className="col-span-2 font-mono text-[11px] text-accent-DEFAULT text-right font-medium">
                    ${Math.round(r.avg_salary_usd / 1000)}K
                  </span>
                  <span className="col-span-1 font-mono text-[10px] text-text-muted text-right">{r.data_points}</span>
                </div>
              ))}
            </div>
          </>
        )}

        {/* ── Skills table ── */}
        {tab === 'skills' && (
          <>
            <div className="grid grid-cols-12 gap-2 px-2 border-b border-border pb-2">
              <ColHeader label="Skill"        sortKey="skill_name"      sort={sort} onSort={handleSort} className="col-span-4" />
              <ColHeader label="Category"     sortKey="skill_category"  sort={sort} onSort={handleSort} className="col-span-3" />
              <ColHeader label="AI Related"   sortKey="is_ai_related"   sort={sort} onSort={handleSort} className="col-span-2 justify-center" />
              <ColHeader label="Growth %"     sortKey="growth_pct"      sort={sort} onSort={handleSort} className="col-span-2 justify-end" />
              <ColHeader label="Demand"       sortKey="avg_demand_score" sort={sort} onSort={handleSort} className="col-span-1 justify-end" />
            </div>
            <div className="space-y-0.5 max-h-96 overflow-y-auto">
              {isLoading ? Array(8).fill(null).map((_, i) => (
                <div key={i} className="h-9 bg-base-700 rounded animate-pulse" />
              )) : skillsFiltered.map(r => (
                <div key={r.skill_name} className="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded-md hover:bg-base-700 transition-colors duration-150">
                  <span className="col-span-4 text-[12px] text-text-primary truncate">{r.skill_name}</span>
                  <span className="col-span-3 font-mono text-[11px] text-text-muted truncate">{r.skill_category}</span>
                  <span className="col-span-2 text-center text-[11px]">
                    {r.is_ai_related
                      ? <span className="font-mono text-[9px] px-1.5 py-0.5 rounded" style={{ background: 'rgba(34,211,238,0.1)', color: '#22D3EE', border: '1px solid rgba(34,211,238,0.2)' }}>AI</span>
                      : <span className="text-text-muted">—</span>}
                  </span>
                  <span className="col-span-2 font-mono text-[11px] text-success text-right">
                    {r.growth_pct != null ? `+${r.growth_pct.toFixed(1)}%` : '—'}
                  </span>
                  <span className="col-span-1 font-mono text-[11px] text-accent-DEFAULT text-right">
                    {r.avg_demand_score?.toFixed(1) ?? '—'}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}

        {/* ── AI Impact table ── */}
        {tab === 'ai-impact' && (
          <>
            <div className="grid grid-cols-12 gap-2 px-2 border-b border-border pb-2">
              <ColHeader label="Role"          sortKey="role_name"           sort={sort} onSort={handleSort} className="col-span-3" />
              <ColHeader label="Category"      sortKey="role_category"       sort={sort} onSort={handleSort} className="col-span-2" />
              <ColHeader label="Level"         sortKey="seniority_level"     sort={sort} onSort={handleSort} className="col-span-2" />
              <ColHeader label="Auto Risk"     sortKey="avg_automation_risk" sort={sort} onSort={handleSort} className="col-span-2 justify-end" />
              <ColHeader label="AI Replace"    sortKey="avg_ai_replacement"  sort={sort} onSort={handleSort} className="col-span-2 justify-end" />
              <ColHeader label="Safe"          sortKey="avg_future_safe"     sort={sort} onSort={handleSort} className="col-span-1 justify-end" />
            </div>
            <div className="space-y-0.5 max-h-96 overflow-y-auto">
              {isLoading ? Array(8).fill(null).map((_, i) => (
                <div key={i} className="h-9 bg-base-700 rounded animate-pulse" />
              )) : aiFiltered.map(r => (
                <div key={`${r.role_name}-${r.seniority_level}`} className="grid grid-cols-12 gap-2 items-center px-2 py-2 rounded-md hover:bg-base-700 transition-colors duration-150">
                  <span className="col-span-3 text-[12px] text-text-primary truncate">{r.role_name}</span>
                  <span className="col-span-2 font-mono text-[11px] text-text-muted truncate">{r.role_category}</span>
                  <span className="col-span-2 font-mono text-[11px] text-text-muted">{r.seniority_level}</span>
                  <span className="col-span-2 font-mono text-[11px] text-danger text-right">
                    {r.avg_automation_risk != null ? `${(r.avg_automation_risk * 100).toFixed(0)}%` : '—'}
                  </span>
                  <span className="col-span-2 font-mono text-[11px] text-warning text-right">
                    {r.avg_ai_replacement != null ? `${(r.avg_ai_replacement * 100).toFixed(0)}%` : '—'}
                  </span>
                  <span className="col-span-1 font-mono text-[11px] text-success text-right">
                    {r.avg_future_safe != null ? `${(r.avg_future_safe * 100).toFixed(0)}%` : '—'}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  )
}