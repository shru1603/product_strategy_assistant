import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'

const COLORS = ['#1565C0','#2E7D32','#F57F17','#6A1B9A','#00838F','#AD1457','#4527A0','#00695C','#558B2F','#E65100']

function Card({ label, value, sub }) {
  return (
    <div style={{ background: '#fff', borderRadius: 10, padding: '16px 20px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)' }}>
      <div style={{ fontSize: 11, color: '#78909C', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.6 }}>{label}</div>
      <div style={{ fontSize: 26, fontWeight: 700, color: '#1565C0', margin: '4px 0 2px' }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: '#90A4AE' }}>{sub}</div>}
    </div>
  )
}

function ChartBox({ title, children }) {
  return (
    <div style={{ background: '#fff', borderRadius: 10, padding: '18px 20px', boxShadow: '0 1px 4px rgba(0,0,0,0.07)' }}>
      <div style={{ fontWeight: 600, fontSize: 13, color: '#37474F', marginBottom: 14 }}>{title}</div>
      {children}
    </div>
  )
}

function toBar(obj) {
  return Object.entries(obj || {}).map(([name, value]) => ({ name, value: Math.round(value) }))
}

const fmt = v => `$${(v / 1000).toFixed(0)}k`
const fmtFull = v => [`$${Number(v).toLocaleString()}`, '']

export default function Dashboard({ result, running, nodes }) {
  if (!result && !running) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '70vh', flexDirection: 'column', gap: 12, color: '#90A4AE' }}>
        <div style={{ fontSize: 52 }}>📊</div>
        <div style={{ fontSize: 17 }}>Upload a CSV file and click Run Analysis</div>
        <div style={{ fontSize: 13 }}>You'll see live charts and KPIs here once the analysis completes</div>
      </div>
    )
  }

  if (running) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '70vh', flexDirection: 'column', gap: 14, color: '#90A4AE' }}>
        <div style={{ fontSize: 52 }}>⚙️</div>
        <div style={{ fontSize: 17 }}>Agents are analyzing your data…</div>
        {nodes.length > 0 && (
          <div style={{ fontSize: 13, background: '#DDE3EA', color: '#1565C0', padding: '8px 18px', borderRadius: 20 }}>
            Latest: {nodes[nodes.length - 1].label}
          </div>
        )}
      </div>
    )
  }

  const raw    = result?.raw_data_summary || {}
  const charts = result?.sales_analysis?.charts_data || {}

  const revenueData  = toBar(charts.revenue_by_product)
  const regionData   = toBar(charts.region_revenue)
  const categoryData = toBar(charts.category_revenue)
  const monthlyData  = toBar(charts.monthly_revenue)
  const marginData   = toBar(charts.margin_by_product)

  const margin = raw.total_revenue ? ((raw.total_profit / raw.total_revenue) * 100).toFixed(1) : '0'
  const retRate = raw.total_units ? ((raw.total_returns / raw.total_units) * 100).toFixed(2) : '0'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* KPI cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
        <Card label="Total Revenue"  value={`$${(raw.total_revenue || 0).toLocaleString()}`}  sub={raw.date_range} />
        <Card label="Total Profit"   value={`$${(raw.total_profit || 0).toLocaleString()}`}   sub={`${margin}% margin`} />
        <Card label="Avg Rating"     value={`${(raw.avg_rating || 0).toFixed(2)} ★`}          sub={`${raw.total_records || 0} records`} />
        <Card label="Return Rate"    value={`${retRate}%`}                                     sub={`${raw.total_returns || 0} of ${raw.total_units || 0} units`} />
      </div>

      {/* Charts row 1 */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 16 }}>
        <ChartBox title="Revenue by Product">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={revenueData} margin={{ bottom: 50 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" interval={0} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={fmt} />
              <Tooltip formatter={fmtFull} />
              <Bar dataKey="value" fill="#1565C0" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartBox>

        <ChartBox title="Revenue by Category">
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={categoryData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={85}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={false} fontSize={10}>
                {categoryData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={fmtFull} />
            </PieChart>
          </ResponsiveContainer>
        </ChartBox>
      </div>

      {/* Charts row 2 */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <ChartBox title="Monthly Revenue Trend">
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={fmt} />
              <Tooltip formatter={fmtFull} />
              <Line type="monotone" dataKey="value" stroke="#1565C0" strokeWidth={2} dot={{ r: 4, fill: '#1565C0' }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartBox>

        <ChartBox title="Revenue by Region">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={regionData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={fmt} />
              <YAxis dataKey="name" type="category" tick={{ fontSize: 12 }} width={56} />
              <Tooltip formatter={fmtFull} />
              <Bar dataKey="value" fill="#2E7D32" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartBox>
      </div>

      {/* Margin chart */}
      <ChartBox title="Average Profit Margin (%) by Product">
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={marginData} margin={{ bottom: 50 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" interval={0} />
            <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `${v}%`} />
            <Tooltip formatter={v => [`${v}%`, 'Margin']} />
            <Bar dataKey="value" fill="#F57F17" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartBox>
    </div>
  )
}
