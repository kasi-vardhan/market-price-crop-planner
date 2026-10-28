import { useState } from 'react'

function App() {
  const [formData, setFormData] = useState({
    farmer_question: '',
    location: 'Markapur',
    soil: 'red',
    water: 'high',
    season: 'kharif',
    land_area: 2,
    budget: '',
  })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === 'land_area' || name === 'budget'
          ? value === '' ? '' : parseFloat(value)
          : value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    const loc = (formData.location || '').trim()
    if (!loc) { setError('Location cannot be empty.'); return }

    const area = Number(formData.land_area)
    if (isNaN(area) || area <= 0 || area > 1000) {
      setError('Land area must be between 0.1 and 1000 acres.')
      return
    }

    const budget = formData.budget === '' ? null : Number(formData.budget)
    if (budget !== null && (isNaN(budget) || budget < 0)) {
      setError('Budget must be a positive number or leave blank for no constraint.')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const payload = {
        location: loc,
        soil: formData.soil,
        water: formData.water,
        season: formData.season,
        land_area: area,
      }
      const question = (formData.farmer_question || '').trim()
      if (question.length >= 3) payload.farmer_question = question
      if (budget !== null) payload.budget = budget

      const response = await fetch('/api/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        let errorMsg = `API request failed with status: ${response.status} ${response.statusText}`
        if (response.status === 502 || response.status === 503) {
          errorMsg = 'Backend server is unreachable. Please make sure the FastAPI backend is running on http://127.0.0.1:8000.'
        } else {
          try {
            const errData = await response.json()
            if (Array.isArray(errData?.detail)) {
              errorMsg = errData.detail
                .map((d) => {
                  const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : ''
                  const fieldLabel = field && field !== 'body' ? `${field.replace(/_/g, ' ')}: ` : ''
                  const cleanMsg = d.msg?.replace(/^Value error,\s*/i, '') || 'Invalid input'
                  return `${fieldLabel}${cleanMsg}`
                })
                .join(' | ')
            } else if (errData?.detail?.errors?.length) {
              errorMsg = errData.detail.errors.join(' | ')
            } else if (errData?.detail?.message) {
              errorMsg = errData.detail.message
            } else if (typeof errData?.detail === 'string') {
              errorMsg = errData.detail
            }
          } catch (_) {}
        }
        throw new Error(errorMsg)
      }

      const data = await response.json()
      console.log('API Result:', data)
      setResult(data)
    } catch (err) {
      console.error('Error:', err)
      setError(err.message || 'Failed to connect to the backend planning service.')
    } finally {
      setLoading(false)
    }
  }

  const fmt = (n) => Number(n).toLocaleString('en-IN')
  const fmtPct = (n) => n !== null && n !== undefined ? `${Number(n).toFixed(1)}%` : 'N/A'

  const getEligibilityBadge = (status) => {
    if (status === 'eligible') return { label: '✅ Eligible', cls: 'badge-eligible' }
    if (status === 'marginal') return { label: '⚠️ Marginal', cls: 'badge-marginal' }
    if (status === 'ineligible') return { label: '❌ Ineligible', cls: 'badge-ineligible' }
    return { label: status || 'Unknown', cls: 'badge-unknown' }
  }

  const getWeatherCondition = (code) => {
    if (code === undefined || code === null) return ''
    if (code === 0) return 'Clear sky'
    if (code <= 3) return 'Partly cloudy'
    if (code <= 48) return 'Foggy'
    if (code <= 67) return 'Rainy'
    if (code <= 77) return 'Snow'
    if (code <= 82) return 'Rain showers'
    if (code >= 95) return 'Thunderstorm'
    return ''
  }

  const rankedCrops = result?.ranking?.ranked_crops || []
  const topCrop = rankedCrops[0] || {}
  const top3 = rankedCrops.slice(0, 3)
  const topProfit = topCrop?.profit || {}
  const compScores = topCrop?.suitability?.component_scores || {}
  const eligBadge = getEligibilityBadge(topCrop?.eligibility_status)
  const marketName = topCrop?.market?.current?.market || 'Andhra Pradesh'
  const pricePerKg = topProfit?.expected_price
  const netProfit = topProfit?.profit
  const roi = topProfit?.roi_percent
  const totalCost = topProfit?.total_cost
  const grossRevenue = topProfit?.revenue
  const breakEven = topProfit?.break_even_price
  const scenarios = topProfit?.scenarios
  const marketStatus = topCrop?.market?.status || topCrop?.data_quality?.market_status || 'cached'

  const confidenceLevel =
    typeof result?.data_confidence === 'object' && result?.data_confidence?.level
      ? result.data_confidence.level
      : typeof result?.data_confidence === 'string'
      ? result.data_confidence
      : 'Standard'

  return (
    <div className="app-container">
      <header className="header">
        <div className="badge">🌱 AI-Powered Agri-Intelligence</div>
        <h1>Market Price &amp; Crop Planning Helper</h1>
        <p>
          Intelligent agricultural decision support combining hyper-local weather, live market
          mandis, agronomic knowledge, and budget-aware crop ranking.
        </p>
      </header>

      <div className="layout-grid">
        {/* ───────── LEFT COLUMN: INPUT FORM ───────── */}
        <div className="card">
          <h2 className="card-title">
            <span>🌾</span> Farm Details
          </h2>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="farmer_question">
                Farmer Query <span style={{ color: '#64748b', fontWeight: 400 }}>(optional)</span>
              </label>
              <textarea
                id="farmer_question"
                name="farmer_question"
                className="form-textarea"
                rows="2"
                value={formData.farmer_question}
                onChange={handleChange}
                placeholder="Ask about a specific crop, price outlook, or constraints... (leave blank for automatic recommendation)"
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label" htmlFor="location">Location (Mandal/District)</label>
                <input
                  id="location"
                  type="text"
                  name="location"
                  className="form-input"
                  value={formData.location}
                  onChange={handleChange}
                  required
                  placeholder="e.g. Markapur, Guntur"
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="land_area">Land Area (Acres)</label>
                <input
                  id="land_area"
                  type="number"
                  step="0.1"
                  min="0.1"
                  name="land_area"
                  className="form-input"
                  value={formData.land_area}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label" htmlFor="soil">Soil Type</label>
                <select id="soil" name="soil" className="form-select" value={formData.soil} onChange={handleChange}>
                  <option value="red">Red Soil</option>
                  <option value="black">Black Soil</option>
                  <option value="alluvial">Alluvial Soil</option>
                  <option value="clay">Clay Soil</option>
                  <option value="loamy">Loamy Soil</option>
                  <option value="sandy">Sandy Soil</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="season">Season</label>
                <select id="season" name="season" className="form-select" value={formData.season} onChange={handleChange}>
                  <option value="kharif">Kharif (Monsoon)</option>
                  <option value="rabi">Rabi (Winter)</option>
                  <option value="zaid">Zaid (Summer)</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="water">Water Availability</label>
              <select id="water" name="water" className="form-select" value={formData.water} onChange={handleChange}>
                <option value="high">High (Assured Irrigation/Canal/Borewell)</option>
                <option value="medium">Medium (Moderate Canal/Seasonal Well)</option>
                <option value="low">Low (Rainfed / Scanty)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="budget">
                Investment Budget (₹) <span style={{ color: '#64748b', fontWeight: 400 }}>(optional)</span>
              </label>
              <input
                id="budget"
                type="number"
                step="1000"
                min="0"
                name="budget"
                className="form-input"
                value={formData.budget}
                onChange={handleChange}
                placeholder="e.g. 50000 — leave blank for no constraint"
              />
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.3rem' }}>
                Crops exceeding this budget will be flagged as over-budget in results.
              </div>
            </div>

            <button
              type="submit"
              id="submit-plan-btn"
              className="btn-primary"
              disabled={loading}
            >
              {loading ? (
                <><span className="spinner">⏳</span> Generating Recommendation...</>
              ) : (
                <><span>🚀</span> Generate Crop Plan</>
              )}
            </button>
          </form>

          {error && (
            <div style={{
              marginTop: '1.25rem',
              padding: '1rem',
              borderRadius: '0.75rem',
              background: 'rgba(244, 63, 94, 0.12)',
              border: '1px solid rgba(244, 63, 94, 0.3)',
              color: '#fb7185',
              fontSize: '0.9rem'
            }}>
              <strong>⚠️ Error:</strong> {error}
            </div>
          )}
        </div>

        {/* ───────── RIGHT COLUMN: RESULTS ───────── */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
            <h2 className="card-title" style={{ margin: 0 }}>
              <span>🌱</span> Crop Planning &amp; Market Insights
            </h2>
            {result && (
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <span className="metric-pill status-live">📍 {result.location || formData.location}</span>
                <span className="metric-pill status-live">✓ Analysis complete</span>
              </div>
            )}
          </div>

          {!result && !loading && (
            <div className="empty-state">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🚜</div>
              <h3>Ready to plan your season</h3>
              <p>Fill in your farm details and click &quot;Generate Crop Plan&quot; to analyze market prices, soil suitability, and weather forecasts.</p>
            </div>
          )}

          {loading && (
            <div className="empty-state">
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🔄</div>
              <h3>Analyzing Agricultural Data...</h3>
              <p>Consulting LangGraph reasoning agent, weather forecasts, market mandis, and RAG knowledge base.</p>
            </div>
          )}

          {result && !loading && (() => {
            return (
              <div>
                {/* ── NO ELIGIBLE CROPS WARNING ── */}
                {result.no_eligible_crops_reason && (
                  <div style={{
                    marginBottom: '1.5rem',
                    padding: '1rem 1.25rem',
                    borderRadius: '0.75rem',
                    background: 'rgba(251, 113, 133, 0.1)',
                    border: '1px solid rgba(251, 113, 133, 0.3)',
                  }}>
                    <div style={{ fontWeight: 700, color: '#fb7185', marginBottom: '0.3rem' }}>⚠️ No Fully Eligible Crops Found</div>
                    <div style={{ fontSize: '0.85rem', color: '#fca5a5' }}>{result.no_eligible_crops_reason}</div>
                  </div>
                )}

                {/* ── 1. BEST RECOMMENDED CROP ── */}
                <div className="result-card-highlight">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
                    <div>
                      <div style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 600 }}>
                        #1 Best Recommended Crop
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.1rem' }}>
                        Ranked by agronomic suitability · affordability · profitability · ROI · market
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                      <span className="metric-pill status-live">
                        Score: {result.recommendation_score != null ? Number(result.recommendation_score).toFixed(1) : 'N/A'}%
                      </span>
                      <span className="metric-pill status-live">
                        Suitability: {topCrop?.suitability?.score != null ? Number(topCrop.suitability.score).toFixed(1) : 'N/A'}%
                      </span>
                      <span className={`metric-pill ${eligBadge.cls}`}>
                        {eligBadge.label}
                      </span>
                    </div>
                  </div>

                  <div style={{ fontSize: '2.4rem', fontWeight: 800, color: '#4ade80', textTransform: 'capitalize', letterSpacing: '-0.02em', margin: '0.4rem 0' }}>
                    {topCrop?.crop || result.recommended_crop || '—'}
                  </div>

                  {/* Cultivation duration */}
                  {topCrop?.suitability?.cultivation_duration_days && (
                    <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '0.75rem' }}>
                      ⏱ Cultivation Duration: {topCrop.suitability.cultivation_duration_days.min}–{topCrop.suitability.cultivation_duration_days.max} days
                    </div>
                  )}

                  {/* Suitability factors */}
                  <div style={{ marginTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '0.85rem' }}>
                    <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.5rem' }}>
                      Agronomic Suitability Factors
                    </div>
                    <div className="factors-grid">
                      {[
                        { label: 'Soil Match', score: compScores.soil, desc: `${formData.soil.toUpperCase()} soil` },
                        { label: 'Water Fit', score: compScores.water, desc: `${formData.water.toUpperCase()} supply` },
                        { label: 'Season', score: compScores.season, desc: `${formData.season.toUpperCase()} window` },
                        { label: 'Temperature', score: compScores.temperature, desc: result.weather?.temperature ? `${result.weather.temperature}°C` : 'N/A' },
                        { label: 'Rainfall', score: compScores.rainfall, desc: result.climate?.average_seasonal_rainfall_mm ? `${result.climate.average_seasonal_rainfall_mm} mm` : 'Historical' },
                      ].map((f, i) => (
                        <div key={i} className="factor-card">
                          <div className="factor-title">{f.label}</div>
                          <div className="factor-score" style={{ color: f.score >= 80 ? '#4ade80' : f.score >= 50 ? '#fbbf24' : '#fb7185' }}>
                            {f.score != null ? `${f.score}%` : 'N/A'}
                          </div>
                          <div className="factor-desc">{f.desc}</div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Ranking reasons */}
                  {topCrop?.reasons?.length > 0 && (
                    <ul style={{ marginTop: '0.75rem', paddingLeft: '1.2rem', fontSize: '0.82rem', color: '#cbd5e1' }}>
                      {topCrop.reasons.map((r, i) => <li key={i}>{r}</li>)}
                    </ul>
                  )}
                </div>

                {/* ── 2. TOP 3 COMPARISON TABLE ── */}
                {top3.length > 1 && (
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
                      📊 Top 3 Crop Comparison
                    </h3>
                    <div style={{ overflowX: 'auto' }}>
                      <table className="comparison-table">
                        <thead>
                          <tr>
                            <th>#</th>
                            <th>Crop</th>
                            <th>Status</th>
                            <th>Score</th>
                            <th>Suitability</th>
                            <th>Investment</th>
                            <th>Gross Rev.</th>
                            <th>Net Profit</th>
                            <th>ROI</th>
                            <th>Market Price</th>
                          </tr>
                        </thead>
                        <tbody>
                          {top3.map((c, i) => {
                            const p = c.profit || {}
                            const eb = getEligibilityBadge(c.eligibility_status)
                            const overBudget = c.budget_exceeded
                            return (
                              <tr key={i} className={i === 0 ? 'row-highlight' : ''}>
                                <td style={{ fontWeight: 700, color: i === 0 ? '#4ade80' : '#94a3b8' }}>#{i + 1}</td>
                                <td style={{ textTransform: 'capitalize', fontWeight: 600 }}>{c.crop}</td>
                                <td>
                                  <span className={`metric-pill ${eb.cls}`} style={{ fontSize: '0.68rem' }}>
                                    {eb.label}
                                  </span>
                                  {overBudget && (
                                    <span className="metric-pill badge-budget" style={{ fontSize: '0.65rem', marginLeft: '0.25rem' }}>
                                      💸 Over Budget
                                    </span>
                                  )}
                                </td>
                                <td style={{ color: '#38bdf8', fontWeight: 700 }}>{fmtPct(c.recommendation_score)}</td>
                                <td>{fmtPct(c.suitability?.score)}</td>
                                <td>{p.total_cost != null ? `₹${fmt(p.total_cost)}` : '—'}</td>
                                <td>{p.revenue != null ? `₹${fmt(p.revenue)}` : '—'}</td>
                                <td style={{ color: p.profit > 0 ? '#4ade80' : p.profit < 0 ? '#fb7185' : '#94a3b8', fontWeight: 700 }}>
                                  {p.profit != null ? `₹${fmt(p.profit)}` : '—'}
                                </td>
                                <td style={{ color: p.roi_percent > 0 ? '#a78bfa' : '#94a3b8' }}>
                                  {p.roi_percent != null ? `${p.roi_percent.toFixed(1)}%` : '—'}
                                </td>
                                <td style={{ fontSize: '0.8rem' }}>
                                  {p.expected_price ? `₹${p.expected_price}/kg` : '—'}
                                </td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                    <div style={{ fontSize: '0.72rem', color: '#475569', marginTop: '0.5rem' }}>
                      * All figures are estimates. Market prices from AGMARKNET cache. Not a guarantee of profit.
                    </div>
                  </div>
                )}

                {/* ── 3. FINANCIAL ANALYSIS (TOP CROP DETAIL) ── */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
                    💰 Financial Analysis — {topCrop?.crop ? topCrop.crop.charAt(0).toUpperCase() + topCrop.crop.slice(1) : 'Top Crop'}
                  </h3>

                  <div className="result-grid">
                    <div className="stat-box">
                      <div className="stat-label">Market Price</div>
                      <div className="stat-value" style={{ fontSize: '1.15rem' }}>
                        {pricePerKg ? <>₹{pricePerKg} <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>/ kg</span></> : <span className="metric-pill status-unavailable">Unavailable</span>}
                      </div>
                      {pricePerKg && <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.2rem' }}>₹{fmt(pricePerKg * 100)} / quintal</div>}
                      <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '0.2rem' }}>{marketName} Mandi</div>
                    </div>

                    <div className="stat-box">
                      <div className="stat-label">Net Profit</div>
                      <div className="stat-value">
                        {netProfit != null ? (
                          <span style={{ color: netProfit >= 0 ? '#4ade80' : '#fb7185' }}>₹{fmt(netProfit)}</span>
                        ) : (
                          <span className="metric-pill status-unavailable">Unavailable</span>
                        )}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.3rem' }}>For {formData.land_area} acres</div>
                    </div>

                    <div className="stat-box">
                      <div className="stat-label">Return on Investment</div>
                      <div className="stat-value" style={{ color: roi > 0 ? '#a78bfa' : '#94a3b8' }}>
                        {roi != null ? `${roi.toFixed(1)}%` : <span className="metric-pill status-unavailable">N/A</span>}
                      </div>
                      {roi != null && (
                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.3rem' }}>
                          {roi > 100 ? 'High ROI — verify price assumptions' : roi > 50 ? 'Good return' : roi > 0 ? 'Positive return' : 'Negative return'}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Financial Breakdown */}
                  <div className="breakdown-box">
                    <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#cbd5e1', marginBottom: '0.5rem' }}>Financial Breakdown</div>
                    {[
                      { label: 'Land Area', value: `${formData.land_area} acres` },
                      { label: 'Expected Yield', value: topProfit?.expected_yield != null ? `${fmt(topProfit.expected_yield)} kg (${(topProfit.expected_yield / 100).toFixed(0)} quintals)` : '—' },
                      { label: 'Market Selling Price', value: pricePerKg ? `₹${pricePerKg}/kg (₹${fmt(pricePerKg * 100)}/quintal)` : 'Unavailable' },
                      { label: 'Cost per kg', value: topProfit?.cost_per_kg != null ? `₹${topProfit.cost_per_kg}/kg` : '—', style: { color: '#f87171' } },
                      { label: 'Break-even Price', value: breakEven != null ? `₹${breakEven}/kg` : '—', style: { color: '#fbbf24' } },
                      { label: 'Estimated Gross Revenue', value: grossRevenue != null ? `₹${fmt(grossRevenue)}` : 'Unavailable', style: { color: '#93c5fd' } },
                      { label: 'Total Cultivation Cost', value: totalCost != null ? `- ₹${fmt(totalCost)} (₹${fmt(topProfit?.cost_per_acre)}/acre)` : '—', style: { color: '#f87171' } },
                    ].map((row, i) => (
                      <div key={i} className="breakdown-row">
                        <span style={{ color: '#94a3b8' }}>{row.label}:</span>
                        <span style={row.style || {}}>{row.value}</span>
                      </div>
                    ))}
                    <div className="breakdown-row" style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '0.5rem', marginTop: '0.25rem' }}>
                      <span style={{ color: '#f1f5f9', fontWeight: 700 }}>Net Estimated Profit:</span>
                      <span style={{ color: netProfit != null && netProfit >= 0 ? '#4ade80' : '#fb7185', fontWeight: 700 }}>
                        {netProfit != null ? `₹${fmt(netProfit)}` : 'Unavailable'}
                      </span>
                    </div>
                    {roi != null && (
                      <div className="breakdown-row">
                        <span style={{ color: '#f1f5f9', fontWeight: 700 }}>ROI:</span>
                        <span style={{ color: '#a78bfa', fontWeight: 700 }}>{roi.toFixed(1)}%</span>
                      </div>
                    )}
                    {result.budget && (
                      <div className="breakdown-row">
                        <span style={{ color: '#94a3b8' }}>Your Budget:</span>
                        <span style={{ color: topCrop?.budget_exceeded ? '#fb7185' : '#4ade80' }}>
                          ₹{fmt(result.budget)} {topCrop?.budget_exceeded ? '⚠️ Cost exceeds budget' : '✅ Within budget'}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Profit Scenarios */}
                  {scenarios && (
                    <div style={{ marginTop: '1rem' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                        📈 Price Scenarios (based on AGMARKNET min/max range)
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
                        {[
                          { key: 'conservative', label: '🔵 Conservative', color: '#60a5fa' },
                          { key: 'expected', label: '🟢 Expected', color: '#4ade80' },
                          { key: 'optimistic', label: '🟡 Optimistic', color: '#fbbf24' },
                        ].map(({ key, label, color }) => {
                          const s = scenarios[key]
                          if (!s) return null
                          return (
                            <div key={key} style={{ background: 'rgba(255,255,255,0.04)', borderRadius: '0.6rem', padding: '0.75rem', border: `1px solid ${color}30` }}>
                              <div style={{ fontSize: '0.75rem', fontWeight: 700, color, marginBottom: '0.4rem' }}>{label}</div>
                              <div style={{ fontSize: '0.82rem', color: '#94a3b8' }}>Price: ₹{s.price}/kg</div>
                              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: s.profit >= 0 ? color : '#fb7185' }}>
                                Profit: ₹{fmt(s.profit)}
                              </div>
                              <div style={{ fontSize: '0.78rem', color: '#64748b' }}>ROI: {s.roi_percent != null ? `${s.roi_percent.toFixed(1)}%` : 'N/A'}</div>
                            </div>
                          )
                        })}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#475569', marginTop: '0.5rem' }}>
                        {scenarios.assumption}
                      </div>
                    </div>
                  )}

                  {/* Market Data Status */}
                  <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    <span className={`metric-pill ${marketStatus === 'live' ? 'status-live' : 'status-cached'}`} style={{ textTransform: 'capitalize' }}>
                      Market Data: {marketStatus}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      Confidence: {confidenceLevel}
                    </span>
                  </div>
                </div>

                {/* ── 4. OTHER CROPS ── */}
                {rankedCrops.length > 3 && (
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
                      🌾 All Evaluated Crops
                    </h3>
                    <div className="runner-up-list">
                      {rankedCrops.slice(3).map((c, idx) => {
                        const eb2 = getEligibilityBadge(c.eligibility_status)
                        return (
                          <div key={idx} className="runner-up-card">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#94a3b8', background: 'rgba(255,255,255,0.06)', padding: '0.2rem 0.5rem', borderRadius: '0.35rem' }}>
                                #{idx + 4}
                              </span>
                              <div>
                                <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f1f5f9', textTransform: 'capitalize' }}>
                                  {c.crop}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                                  <span className={`metric-pill ${eb2.cls}`} style={{ fontSize: '0.65rem', marginRight: '0.3rem' }}>{eb2.label}</span>
                                  Suitability: {c.suitability?.score != null ? `${c.suitability.score}%` : 'N/A'}
                                  {c.budget_exceeded && ' · ⚠️ Over budget'}
                                </div>
                              </div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                              <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#38bdf8' }}>
                                {fmtPct(c.recommendation_score)}
                              </div>
                              <div style={{ fontSize: '0.72rem', color: '#64748b' }}>
                                Profit: {c.profit?.profit != null ? `₹${fmt(c.profit.profit)}` : 'N/A'}
                                {c.profit?.roi_percent != null ? ` · ROI: ${c.profit.roi_percent.toFixed(1)}%` : ''}
                              </div>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}

                {/* ── 5. WEATHER ── */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
                    ⛅ Weather &amp; Climate
                  </h3>
                  <div className="result-grid">
                    <div className="stat-box">
                      <div className="stat-label">Current Temperature</div>
                      <div className="stat-value" style={{ fontSize: '1.15rem' }}>
                        {result.weather?.temperature !== undefined ? `${result.weather.temperature}°C` : '—'}
                        {' '}<span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                          {result.weather?.condition || getWeatherCondition(result.weather?.weather_code) || ''}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>
                        Rainfall: {result.weather?.daily_rainfall ?? result.weather?.precipitation ?? 0} mm
                      </div>
                    </div>
                    <div className="stat-box">
                      <div className="stat-label">Historical Seasonal Rain</div>
                      <div className="stat-value" style={{ fontSize: '1.05rem' }}>
                        {result.climate?.average_seasonal_rainfall_mm != null ? `${result.climate.average_seasonal_rainfall_mm} mm` : '—'}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>
                        {result.climate?.years_analyzed ? `${result.climate.years_analyzed}-year average` : formData.season.toUpperCase()} season
                      </div>
                    </div>
                    <div className="stat-box">
                      <div className="stat-label">Weather Source</div>
                      <div style={{ marginTop: '0.3rem' }}>
                        <span className={`metric-pill ${result.weather?.status === 'live' ? 'status-live' : 'status-cached'}`}>
                          {result.weather?.status || 'Active'}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '0.4rem' }}>
                        {result.weather?.source || 'Open-Meteo Weather API'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* ── 6. AI RECOMMENDATION ── */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
                    📋 AI Synthesis &amp; Recommendation
                  </h3>
                  <div className="markdown-body" style={{ background: 'rgba(15,23,42,0.4)', padding: '1rem 1.25rem', borderRadius: '0.75rem', border: '1px solid rgba(255,255,255,0.05)', whiteSpace: 'pre-line' }}>
                    {result.recommendation || 'Generating analysis...'}
                  </div>
                </div>

                {/* ── 7. SOURCES ── */}
                {result.sources?.length > 0 && (
                  <div style={{ marginTop: '1.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                      <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0' }}>
                        📚 Agricultural Evidence &amp; Sources
                      </h3>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Retrieved RAG Documents</span>
                    </div>
                    {result.sources.map((src, idx) => (
                      <div key={idx} className="evidence-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', flexWrap: 'wrap' }}>
                          <div>
                            <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f1f5f9' }}>
                              📄 {src.title || src.document || 'Agricultural Guidance Advisory'}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.15rem' }}>
                              {src.organization || 'Indian Council of Agricultural Research'}
                            </div>
                          </div>
                          {src.crop && (
                            <span className="metric-pill status-live" style={{ fontSize: '0.7rem' }}>{src.crop}</span>
                          )}
                        </div>
                        {src.passage && (
                          <div className="evidence-passage">"{src.passage}"</div>
                        )}
                        {src.url && (
                          <a href={src.url} target="_blank" rel="noopener noreferrer" className="evidence-link">
                            <span>🔗 Verified Source:</span> {src.url} ↗
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })()}
        </div>
      </div>
    </div>
  )
}

export default App
