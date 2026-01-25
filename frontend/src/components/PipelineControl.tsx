import { useState, useEffect } from 'react'
import { usePipelineControlStore } from '../stores/pipelineControlStore'
import { usePipelineWebSocket } from '../hooks/useWebSocket'
import { usePipelineStore } from '../stores/websocketStore'

export function PipelineControl() {
  const [pipelineName, setPipelineName] = useState('')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [selectionMethod, setSelectionMethod] = useState('range')
  const [tabletCount, setTabletCount] = useState(50)
  const [rangeStart, setRangeStart] = useState(254200)
  const [period, setPeriod] = useState('Ur III')
  const control = usePipelineControlStore()
  const pipeline = usePipelineStore()

  useEffect(() => {
    control.fetchRuns()
  }, [])

  usePipelineWebSocket(control.currentRun?.id)

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const run = await control.startPipeline(
        pipelineName || 'Pipeline Run',
        {
          skip_download: false,
          skip_annotation: false,
          selection_method: selectionMethod,
          tablet_count: tabletCount,
          range_start: rangeStart,
          period: period,
          epochs: 10,
          batch_size: 32,
        }
      )
      setPipelineName('')
      setIsFormOpen(false)
      // Subscribe to WebSocket updates
      pipeline.setRunId(run.id)
    } catch (error) {
      console.error('Failed to start pipeline:', error)
    }
  }

  const handleCancel = async () => {
    if (!control.currentRun) return
    try {
      await control.cancelPipeline(control.currentRun.id)
    } catch (error) {
      console.error('Failed to cancel pipeline:', error)
    }
  }

  const isRunning = control.currentRun?.status === 'running'
  const isPending = control.currentRun?.status === 'pending'
  const isActive = isRunning || isPending

  return (
    <div className="space-y-6">
      {/* Start Pipeline Form */}
      {!isActive && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Start Pipeline</h2>

          {!isFormOpen ? (
            <button
              onClick={() => setIsFormOpen(true)}
              className="w-full btn-primary py-3 text-lg"
            >
              ▶ Start New Pipeline
            </button>
          ) : (
            <form onSubmit={handleStart} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Pipeline Name
                </label>
                <input
                  type="text"
                  value={pipelineName}
                  onChange={(e) => setPipelineName(e.target.value)}
                  placeholder="e.g., Ur III Collection Download"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tablet Selection Method
                </label>
                <select
                  value={selectionMethod}
                  onChange={(e) => setSelectionMethod(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="range">📊 Range (Sequential P-numbers)</option>
                  <option value="search">🔍 Search (By Period/Criteria)</option>
                  <option value="random">🎲 Random (From CDLI Collection)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of Tablets
                </label>
                <input
                  type="number"
                  value={tabletCount}
                  onChange={(e) => setTabletCount(parseInt(e.target.value) || 50)}
                  min="1"
                  max="500"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Recommended: 10-100 tablets per run
                </p>
              </div>

              {selectionMethod === 'range' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Starting P-number
                  </label>
                  <input
                    type="number"
                    value={rangeStart}
                    onChange={(e) => setRangeStart(parseInt(e.target.value) || 254200)}
                    min="100000"
                    max="500000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Will download P{rangeStart} to P{rangeStart + tabletCount - 1}
                  </p>
                </div>
              )}

              {selectionMethod === 'search' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Period
                  </label>
                  <select
                    value={period}
                    onChange={(e) => setPeriod(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Ur III">Ur III (2112-2004 BCE)</option>
                    <option value="Old Babylonian">Old Babylonian (2004-1595 BCE)</option>
                    <option value="Old Akkadian">Old Akkadian (2350-2150 BCE)</option>
                    <option value="Early Dynastic">Early Dynastic (2900-2350 BCE)</option>
                    <option value="Neo-Assyrian">Neo-Assyrian (911-609 BCE)</option>
                    <option value="Neo-Babylonian">Neo-Babylonian (626-539 BCE)</option>
                  </select>
                </div>
              )}

              <div className="grid grid-cols-2 gap-2 pt-2">
                <button
                  type="submit"
                  disabled={control.isStarting}
                  className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {control.isStarting ? '⏳ Starting...' : '✓ Start'}
                </button>
                <button
                  type="button"
                  onClick={() => setIsFormOpen(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {control.error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 rounded text-red-800 text-sm">
              {control.error}
            </div>
          )}
        </div>
      )}

      {/* Active Pipeline Status */}
      {isActive && control.currentRun && (
        <div className="card border-2 border-blue-500">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {control.currentRun.name}
              </h2>
              <p className="text-sm text-gray-600">ID: {control.currentRun.id}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Status</p>
              <p
                className={`text-lg font-bold ${isRunning ? 'text-green-600' : 'text-amber-600'
                  }`}
              >
                {control.currentRun.status.toUpperCase()}
              </p>
            </div>
          </div>

          {/* Overall Progress */}
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Overall Progress</span>
              <span className="text-sm font-semibold text-gray-900">{pipeline.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${pipeline.progress}%` }}
              />
            </div>
          </div>

          {/* Current Step */}
          {pipeline.currentStep && (
            <div className="mb-4 p-3 bg-blue-50 rounded border border-blue-200">
              <p className="text-sm text-gray-600 mb-1">Current Step</p>
              <p className="font-semibold text-gray-900">{pipeline.currentStep}</p>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all"
                  style={{ width: `${pipeline.stepProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Metrics */}
          {Object.keys(pipeline.metrics).length > 0 && (
            <div className="mb-4 p-3 bg-gray-50 rounded border border-gray-200">
              <p className="text-sm text-gray-600 mb-2">Live Metrics</p>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(pipeline.metrics).map(([key, value]) => (
                  <div key={key} className="bg-white p-2 rounded border">
                    <p className="text-xs text-gray-600">{key}</p>
                    <p className="text-lg font-bold text-gray-900">
                      {typeof value === 'number' ? value.toFixed(4) : value}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Status Message */}
          {pipeline.statusMessage && (
            <div className="mb-4 p-3 bg-amber-50 rounded border border-amber-200">
              <p className="text-sm text-amber-900">{pipeline.statusMessage}</p>
            </div>
          )}

          {/* Error Display */}
          {pipeline.lastError && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 rounded text-red-800 text-sm">
              <p className="font-semibold">Error</p>
              <p>{pipeline.lastError}</p>
            </div>
          )}

          {/* Logs */}
          {pipeline.logs.length > 0 && (
            <div className="mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Recent Logs ({pipeline.logs.length})</p>
              <div className="bg-gray-900 text-gray-100 p-3 rounded font-mono text-xs max-h-40 overflow-y-auto space-y-1">
                {pipeline.logs.slice(-20).map((log, idx) => (
                  <div
                    key={idx}
                    className={`${log.level === 'error'
                      ? 'text-red-400'
                      : log.level === 'warning'
                        ? 'text-amber-400'
                        : 'text-green-400'
                      }`}
                  >
                    <span className="text-gray-500">[{log.level.toUpperCase()}]</span> {log.message}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Control Buttons */}
          <div className="flex gap-2">
            <button
              onClick={() => setIsFormOpen(true)}
              className="flex-1 btn-secondary"
              disabled={!isRunning}
            >
              ⏸ Pause
            </button>
            <button
              onClick={handleCancel}
              disabled={control.isCancelling || !isActive}
              className="flex-1 btn-danger disabled:opacity-50 disabled:cursor-not-allowed bg-red-600 hover:bg-red-700 text-white font-semibold py-2 rounded-lg"
            >
              {control.isCancelling ? '⏳...' : '⏹ Cancel'}
            </button>
          </div>
        </div>
      )}

      {/* Recent Runs */}
      {control.runs.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Runs</h2>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {control.runs.slice(0, 5).map((run) => (
              <div key={run.id} className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{run.name}</p>
                  <p className="text-xs text-gray-500">ID: {run.id}</p>
                </div>
                <div className="text-right">
                  <span
                    className={`inline-block px-2 py-1 text-xs font-semibold rounded ${run.status === 'completed'
                      ? 'bg-green-100 text-green-800'
                      : run.status === 'failed'
                        ? 'bg-red-100 text-red-800'
                        : run.status === 'running'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                  >
                    {run.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
