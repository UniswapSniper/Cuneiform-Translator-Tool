import { PipelineControl as PipelineControlComponent } from '../components/PipelineControl'

export default function PipelineControl() {
  return (
    <div className="page-container">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Pipeline Control</h1>
      <PipelineControlComponent />
    </div>
  )
}
