import { useState, useRef } from 'react'
import { API_BASE_URL, isApiAvailable, reportApiSuccess, reportApiFailure } from '../lib/constants'

interface UploadedTablet {
    id: number
    pnumber: string
    name: string
    image_path: string
}

interface TabletUploadProps {
    onUploadSuccess?: (tablet: UploadedTablet) => void
}

export function TabletUpload({ onUploadSuccess }: TabletUploadProps) {
    const [isDragging, setIsDragging] = useState(false)
    const [isUploading, setIsUploading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [success, setSuccess] = useState<string | null>(null)
    const [preview, setPreview] = useState<string | null>(null)
    const [tabletName, setTabletName] = useState('')
    const [period, setPeriod] = useState('')
    const [description, setDescription] = useState('')
    const fileInputRef = useRef<HTMLInputElement>(null)
    const [selectedFile, setSelectedFile] = useState<File | null>(null)

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(true)
    }

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setIsDragging(false)

        const files = e.dataTransfer.files
        if (files.length > 0) {
            handleFileSelect(files[0])
        }
    }

    const handleFileSelect = (file: File) => {
        // Validate file type
        const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp', 'image/tiff']
        if (!validTypes.includes(file.type)) {
            setError('Invalid file type. Please upload PNG, JPG, GIF, WebP, or TIFF.')
            return
        }

        // Validate file size (max 50MB)
        if (file.size > 50 * 1024 * 1024) {
            setError('File too large. Maximum size is 50MB.')
            return
        }

        setSelectedFile(file)
        setError(null)
        setSuccess(null)

        // Create preview
        const reader = new FileReader()
        reader.onload = (e) => {
            setPreview(e.target?.result as string)
        }
        reader.readAsDataURL(file)

        // Set default name from filename
        if (!tabletName) {
            setTabletName(file.name.replace(/\.[^/.]+$/, ''))
        }
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files
        if (files && files.length > 0) {
            handleFileSelect(files[0])
        }
    }

    const handleUpload = async () => {
        if (!selectedFile || !isApiAvailable() || !API_BASE_URL) {
            setError('No file selected or backend unavailable')
            return
        }

        setIsUploading(true)
        setError(null)

        try {
            const formData = new FormData()
            formData.append('file', selectedFile)
            formData.append('name', tabletName || selectedFile.name)
            formData.append('period', period || 'Unknown')
            formData.append('description', description)

            const response = await fetch(`${API_BASE_URL}/tablets/upload`, {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                const data = await response.json()
                throw new Error(data.error || `Upload failed: ${response.status}`)
            }

            const data = await response.json()
            reportApiSuccess()

            setSuccess(`Tablet "${data.tablet.name}" uploaded successfully! (${data.tablet.pnumber})`)
            setSelectedFile(null)
            setPreview(null)
            setTabletName('')
            setPeriod('')
            setDescription('')

            if (onUploadSuccess) {
                onUploadSuccess(data.tablet)
            }
        } catch (err) {
            reportApiFailure()
            setError(err instanceof Error ? err.message : 'Upload failed')
        } finally {
            setIsUploading(false)
        }
    }

    const handleClear = () => {
        setSelectedFile(null)
        setPreview(null)
        setTabletName('')
        setPeriod('')
        setDescription('')
        setError(null)
        setSuccess(null)
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }

    return (
        <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">📤 Upload Tablet Image</h2>

            {/* Drop Zone */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all
          ${isDragging
                        ? 'border-blue-500 bg-blue-50'
                        : preview
                            ? 'border-green-400 bg-green-50'
                            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                    }
        `}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleInputChange}
                    className="hidden"
                />

                {preview ? (
                    <div className="space-y-4">
                        <img
                            src={preview}
                            alt="Preview"
                            className="max-h-48 mx-auto rounded-lg shadow-md"
                        />
                        <p className="text-sm text-green-700 font-medium">
                            ✓ {selectedFile?.name}
                        </p>
                    </div>
                ) : (
                    <div className="space-y-2">
                        <div className="text-4xl">📜</div>
                        <p className="text-gray-600 font-medium">
                            Drag & drop a tablet image here
                        </p>
                        <p className="text-sm text-gray-500">
                            or click to browse (PNG, JPG, GIF, WebP, TIFF)
                        </p>
                    </div>
                )}
            </div>

            {/* Metadata Form */}
            {selectedFile && (
                <div className="mt-4 space-y-3">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Tablet Name
                        </label>
                        <input
                            type="text"
                            value={tabletName}
                            onChange={(e) => setTabletName(e.target.value)}
                            placeholder="e.g., Royal Inscription Fragment"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Period (optional)
                        </label>
                        <select
                            value={period}
                            onChange={(e) => setPeriod(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="">Unknown</option>
                            <option value="Uruk">Uruk (4000-3100 BCE)</option>
                            <option value="Early Dynastic">Early Dynastic (2900-2350 BCE)</option>
                            <option value="Old Akkadian">Old Akkadian (2350-2150 BCE)</option>
                            <option value="Ur III">Ur III (2112-2004 BCE)</option>
                            <option value="Old Babylonian">Old Babylonian (2004-1595 BCE)</option>
                            <option value="Middle Babylonian">Middle Babylonian (1595-1000 BCE)</option>
                            <option value="Neo-Assyrian">Neo-Assyrian (911-609 BCE)</option>
                            <option value="Neo-Babylonian">Neo-Babylonian (626-539 BCE)</option>
                            <option value="Achaemenid">Achaemenid (539-330 BCE)</option>
                            <option value="Seleucid">Seleucid (330-63 BCE)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Description (optional)
                        </label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Any notes about this tablet..."
                            rows={2}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div className="flex gap-2 pt-2">
                        <button
                            onClick={handleUpload}
                            disabled={isUploading}
                            className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isUploading ? '⏳ Uploading...' : '📤 Upload Tablet'}
                        </button>
                        <button
                            onClick={handleClear}
                            className="btn-secondary"
                        >
                            Clear
                        </button>
                    </div>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className="mt-4 p-3 bg-red-100 border border-red-400 rounded-lg text-red-800 text-sm">
                    ❌ {error}
                </div>
            )}

            {/* Success Message */}
            {success && (
                <div className="mt-4 p-3 bg-green-100 border border-green-400 rounded-lg text-green-800 text-sm">
                    ✅ {success}
                </div>
            )}
        </div>
    )
}
