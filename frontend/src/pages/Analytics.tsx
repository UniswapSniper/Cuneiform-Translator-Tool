import { Card } from '../components/Card'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export default function Analytics() {
  const trainingData = [
    { epoch: 1, loss: 0.8, mAP: 0.45 },
    { epoch: 2, loss: 0.6, mAP: 0.52 },
    { epoch: 3, loss: 0.45, mAP: 0.68 },
    { epoch: 4, loss: 0.35, mAP: 0.78 },
    { epoch: 5, loss: 0.28, mAP: 0.84 },
  ]

  const qualityData = [
    { name: 'Pass', value: 245 },
    { name: 'Warning', value: 58 },
    { name: 'Fail', value: 21 },
  ]

  const COLORS = ['#10b981', '#f59e0b', '#ef4444']

  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Analytics & Research Hub</h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <p className="text-gray-600 font-medium">Models Trained</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">12</p>
          <p className="text-sm text-green-600 mt-2">+2 this week</p>
        </Card>
        <Card>
          <p className="text-gray-600 font-medium">Avg mAP Score</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">0.847</p>
          <p className="text-sm text-green-600 mt-2">+0.032 improvement</p>
        </Card>
        <Card>
          <p className="text-gray-600 font-medium">Total Tablets</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">324</p>
          <p className="text-sm text-green-600 mt-2">+50 this month</p>
        </Card>
        <Card>
          <p className="text-gray-600 font-medium">Pipeline Runs</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">156</p>
          <p className="text-sm text-green-600 mt-2">+12 success rate</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Training Curves */}
        <Card title="Training Metrics Over Time">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trainingData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="epoch" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="loss"
                stroke="#ef4444"
                name="Loss"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="mAP"
                stroke="#10b981"
                name="mAP"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        {/* Quality Distribution */}
        <Card title="Tablet Quality Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={qualityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {qualityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  )
}
