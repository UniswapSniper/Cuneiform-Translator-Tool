# Web UI Master Plan - Cuneiform Translator
## Step 5 / M3: Interactive Web Interface for Sign Detection Pipeline

**Status**: 🎨 Design Phase (Ready for Implementation)  
**Scope**: Comprehensive web interface for ML pipeline orchestration + visualization  
**Complexity**: High (Advanced graphics, animations, real-time monitoring)  
**Estimated Timeline**: 2-3 weeks for full implementation  

---

## 📋 Executive Summary

Build a **beautiful, intuitive, production-grade web interface** that makes the cuneiform sign detection pipeline accessible to researchers, students, and collaborators. The UI will elegantly wrap our orchestrator backend with:

- 🎬 **Real-time pipeline monitoring** with animated progress
- 📊 **Advanced data visualization** (interactive charts, comparisons, metrics)
- 🖼️ **Tablet gallery** with annotation viewer and detection overlays
- 🤖 **Model management** dashboard with comparison tools
- 📈 **Research metrics** tracking and export
- ✨ **Elegant animations** that guide user through workflows

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                     USER BROWSER                            │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              React Frontend (TypeScript)               │  │
│  │  ┌──────────────────────────────────────────────────┐  │  │
│  │  │ Features:                                        │  │  │
│  │  │ • Pages & Routes                                 │  │  │
│  │  │ • Interactive Charts (Recharts)                  │  │  │
│  │  │ • Real-time Updates (WebSocket)                  │  │  │
│  │  │ • Animation Library (Framer Motion)              │  │  │
│  │  │ • Image Gallery (React Photo Album)              │  │  │
│  │  │ • Responsive Design (Tailwind CSS)               │  │  │
│  │  │ • State Management (Zustand)                     │  │  │
│  │  └──────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────┘  │
│                            ↕  (HTTP + WebSocket)             │
├──────────────────────────────────────────────────────────────┤
│                   BACKEND SERVER (Flask)                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ API Endpoints:                                         │  │
│  │ • /api/pipeline/* (control orchestrator)              │  │
│  │ • /api/models/* (list, compare, delete)               │  │
│  │ • /api/tablets/* (gallery, annotations, detection)    │  │
│  │ • /api/metrics/* (training results, statistics)       │  │
│  │ • /api/websocket (real-time progress)                 │  │
│  │ • /api/export/* (download results, models)            │  │
│  └────────────────────────────────────────────────────────┘  │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │      Orchestrator Backend (Python)                    │  │
│  │  run_complete_pipeline.py                             │  │
│  │  (Already built and tested!)                          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
          ↓                                    ↓
    ┌──────────────────────────────────────────────┐
    │         Data & Models                        │
    │ /data, /models, pipeline_report.json         │
    └──────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend
| Component | Technology | Why |
|-----------|-----------|-----|
| **Framework** | React 18 + TypeScript | Modern, type-safe, component-based |
| **Styling** | Tailwind CSS | Utility-first, fast iteration, beautiful defaults |
| **State Management** | Zustand | Lightweight, simple, performant |
| **Charts** | Recharts | React-friendly, beautiful, customizable |
| **Animations** | Framer Motion | Smooth, declarative animations |
| **Image Gallery** | React Photo Album | Responsive, touch-friendly, professional |
| **Icons** | Heroicons | Clean, consistent, accessible |
| **UI Components** | Radix UI (optional) | Headless, accessible, customizable |
| **Real-time** | Socket.IO | WebSocket for live progress updates |
| **Build** | Vite | Fast dev, optimized build |
| **Testing** | Vitest + Testing Library | Fast, comprehensive testing |

### Backend
| Component | Technology | Why |
|-----------|-----------|-----|
| **Framework** | Flask + Flask-CORS | Lightweight, Python-native, extensible |
| **WebSocket** | Flask-SocketIO | Real-time bidirectional communication |
| **Task Queue** | Celery + Redis | Background job processing, progress tracking |
| **API** | Flask-RESTful | Clean REST endpoints |
| **Async** | Threading/Asyncio | Parallel processing without blocking |
| **Image Processing** | OpenCV + Pillow | Already used, familiar |
| **Database** | SQLite | Lightweight, built-in Python, metadata tracking |

---

## 📱 Page Structure & Features

### 1. **Dashboard Home Page** ✨
**Purpose**: First impression, quick overview of system status

**Layout**:
```
┌─────────────────────────────────────────────────────┐
│  CUNEIFORM TRANSLATOR                          [⚙️] │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Welcome back, Researcher! 👋                       │
│                                                     │
│  ┌──────────────┬──────────────┬──────────────┐    │
│  │ Tablets      │ Models       │ Annotations  │    │
│  │ 342 total    │ 5 trained    │ 287 regions  │    │
│  │ 45 new       │ 2 comparing  │ 95% quality  │    │
│  └──────────────┴──────────────┴──────────────┘    │
│                                                     │
│  Recent Activity (animated timeline):              │
│  ─────────────────────────────────────────────     │
│  ✓ Model "baseline-v3" completed         2h ago   │
│  ⏳ Training "aug-large-50ep"              5% done  │
│  📊 Comparison "v3-vs-v4" ready                     │
│  📥 Downloaded 50 CDLI tablets            yesterday │
│                                                     │
│  Quick Actions:                                    │
│  [New Training] [View Results] [Annotate] [Export] │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Features**:
- ✨ Animated progress indicators
- 📊 Stat cards with icons
- 🎬 Timeline of recent activities (animated)
- 🔄 Live status updates (WebSocket)
- 🎯 Quick action buttons

---

### 2. **Pipeline Control Page** 🎮
**Purpose**: Launch and monitor training runs

**Layout**:
```
┌────────────────────────────────────────────────────┐
│ Training Dashboard                            [×]  │
├────────────────────────────────────────────────────┤
│                                                    │
│ ACTIVE TRAINING: YOLOv8-Medium (Baseline)        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 35% [⏸] [✕]   │
│ Epoch 18/50 | Batch 145/2340 | ETA 1h 32m       │
│                                                    │
│ Live Metrics Chart:                               │
│ ┌──────────────────────────────────────────────┐  │
│ │                                              │  │
│ │  Loss ↓          mAP ↑        Accuracy ↑   │  │
│ │   █ ╲                █ ╱           █ ╱      │  │
│ │   │  ╲              │ ╱            │ ╱       │  │
│ │   │   ╲ ╲          │╱             │╱        │  │
│ │   │    ╲ ╲        ╱              ╱          │  │
│ │   │     ╲ ╲      ╱              ╱           │  │
│ │   └─────╱─────────────────────────────      │  │
│ └──────────────────────────────────────────────┘  │
│                                                    │
│ Configuration:                                    │
│ • 3D Augmentation: ON ✓    • Device: MPS         │
│ • Batch Size: 16           • Epochs: 50          │
│ • Learning Rate: 0.001                           │
│                                                    │
│ GPU Memory: ████████░░ 78%  |  FPS: 45          │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Subpages/Modals**:

#### **2a. New Training Configuration**
```
Advanced Options:
┌─────────────────────────────────────┐
│ Model Size: [Nano ▼]                │
│ Epochs: [50]                        │
│ Batch Size: [16]                    │
│ Learning Rate: [0.001]              │
│ Device: [MPS ▼]                     │
│ ☑ Enable 3D Augmentation           │
│ ☑ Train Baseline (for comparison)   │
│ ☐ Use Custom Dataset                │
└─────────────────────────────────────┘
```

#### **2b. Training Queue**
```
Queued Trainings:
1. YOLOv8-Small + Augmentation (started)
2. YOLOv8-Medium + Augmentation (queued)
3. Baseline Comparison (queued)
4. Test Run - 5 epochs (queued)
```

---

### 3. **Model Gallery & Comparison** 🏆
**Purpose**: View trained models, compare performance

**Layout**:
```
┌────────────────────────────────────────────────────┐
│ Models                                         [+] │
├────────────────────────────────────────────────────┤
│                                                    │
│ View: [All] [Trained] [Comparing] [Archived]     │
│                                                    │
│ Model Cards (grid layout):                        │
│                                                    │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│ │ Baseline │  │ Aug-v2   │  │ Aug-v3   │        │
│ │ ★★★★☆   │  │ ★★★★★   │  │ ★★★★★   │        │
│ │ mAP:0.742│  │ mAP:0.798│  │ mAP:0.823│        │
│ │ 2h 34m   │  │ 2h 51m   │  │ 3h 12m   │        │
│ │ [Compare]│  │ [Compare]│  │ [Use]    │        │
│ │ [Delete] │  │ [Delete] │  │ [Delete] │        │
│ └──────────┘  └──────────┘  └──────────┘        │
│                                                    │
│ Model Comparison (detailed view):                 │
│ ┌────────────────────────────────────────────┐   │
│ │                                            │   │
│ │  Performance Comparison                   │   │
│ │  ┌─────────────────────────────────────┐  │   │
│ │  │ mAP                                 │  │   │
│ │  │        Baseline    Aug-v2    Aug-v3 │  │   │
│ │  │        74.2%   →   79.8%  →  82.3% │  │   │
│ │  │         ├─────────┤                 │  │   │
│ │  │         +7.6%     +10.9%            │  │   │
│ │  │                                     │  │   │
│ │  │ Training Time                       │  │   │
│ │  │        2h34m       2h51m     3h12m  │  │   │
│ │  │                                     │  │   │
│ │  │ Model Size                          │  │   │
│ │  │        45 MB       45 MB      45 MB │  │   │
│ │  └─────────────────────────────────────┘  │   │
│ │                                            │   │
│ └────────────────────────────────────────────┘   │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Features**:
- 📊 Side-by-side performance comparison
- 📈 Metrics charts (mAP, loss curves)
- ⚡ Model size and inference speed comparison
- 🎯 Visual performance indicators (star ratings)
- 💾 Download/archive models
- 🏷️ Tagging and notes for each model

---

### 4. **Tablet Gallery** 🖼️
**Purpose**: Browse, annotate, view detection results

**Layout**:
```
┌────────────────────────────────────────────────────┐
│ Tablet Library                                  [🔍] │
├────────────────────────────────────────────────────┤
│                                                    │
│ Filters: [All] [CDLI] [User Upload] [Annotated]  │
│ Sort: [Recent] [Alphabetical] [Quality]           │
│ Search: [Search tablets...                    ]   │
│                                                    │
│ Photo Gallery (responsive grid):                  │
│                                                    │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │
│ │      │ │      │ │      │ │      │            │
│ │ P001 │ │ P002 │ │ P003 │ │ P004 │            │
│ │ ✓✓✓  │ │ ✓✓   │ │ ✓    │ │ ✓✓✓  │            │
│ └──────┘ └──────┘ └──────┘ └──────┘            │
│                                                    │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │
│ │      │ │      │ │      │ │      │            │
│ │ P005 │ │ P006 │ │ P007 │ │ P008 │            │
│ │ ✓✓✓  │ │      │ │ ✓✓✓  │ │ ✓    │            │
│ └──────┘ └──────┘ └──────┘ └──────┘            │
│                                                    │
│ Tablet Details (click on image):                  │
│ ┌──────────────────────────────────────────────┐  │
│ │ P100100                                      │  │
│ │ ┌────────────────────────────────────────┐   │  │
│ │ │                                        │   │  │
│ │ │         [Tablet Image]                 │   │  │
│ │ │      with Detected Regions             │   │  │
│ │ │                                        │   │  │
│ │ └────────────────────────────────────────┘   │  │
│ │                                              │  │
│ │ Annotations: 23 regions                      │  │
│ │ • Annotator 1 (95% agreement)                │  │
│ │ • Annotator 2 (92% agreement)                │  │
│ │ • Model Predictions (87% confidence)         │  │
│ │                                              │  │
│ │ [Edit Annotations] [View History] [Export]   │  │
│ └──────────────────────────────────────────────┘  │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Features**:
- 🎨 Responsive photo gallery (masonry layout)
- 🔍 Search and filter capabilities
- 📸 Lightbox viewer with annotations overlay
- ✏️ Inline annotation editor
- 🤖 Model prediction visualization
- 📊 Agreement metrics between annotators
- 📥 Download/export individual tablets

---

### 5. **Detection Inspector** 🔬
**Purpose**: Upload image and see sign detection results

**Layout**:
```
┌────────────────────────────────────────────────────┐
│ Detect Signs                                       │
├────────────────────────────────────────────────────┤
│                                                    │
│ Drop image here or [Browse]                       │
│ (Supported: JPG, PNG, TIFF)                       │
│                                                    │
│ Select Model:                                     │
│ ○ Latest (aug-v3, mAP:0.823)                      │
│ ○ Baseline (mAP:0.742)                            │
│ ○ Custom...                                       │
│                                                    │
│ [Detect]                                          │
│                                                    │
│ Results:                                          │
│ ┌────────────────────────────────────────────────┐│
│ │                                               ││
│ │     [Original Image]    [Overlay View]       ││
│ │                                               ││
│ │  Detected: 47 signs                           ││
│ │  Confidence: 0.89 avg                         ││
│ │                                               ││
│ └────────────────────────────────────────────────┘│
│                                                    │
│ Results Table:                                    │
│ │ Sign   │ Confidence │ Location   │ Class     │  │
│ │───────────────────────────────────────────── │  │
│ │ A-1    │ 0.95       │ (124, 340) │ Personnel │  │
│ │ B-2    │ 0.92       │ (456, 201) │ Commodity │  │
│ │ ...                                          │  │
│                                                    │
│ [Download JSON] [Download CSV] [Save to Gallery] │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Features**:
- 📤 Drag-and-drop image upload
- 🎯 Real-time detection visualization
- 📊 Results table with sortable columns
- 🎨 Multiple visualization modes (overlay, heatmap, annotations)
- 💾 Export results in multiple formats
- 🏷️ Confidence filtering

---

### 6. **Analytics & Research Hub** 📊
**Purpose**: Deep dive into training metrics and research insights

**Layout**:
```
┌────────────────────────────────────────────────────┐
│ Research Analytics                                 │
├────────────────────────────────────────────────────┤
│                                                    │
│ Training History:                                  │
│ ┌────────────────────────────────────────────────┐│
│ │                                               ││
│ │  mAP Over Time                                ││
│ │      ↑                                        ││
│ │   85%├─────── Aug-v3 (82.3%)                ││
│ │      │╭─╮╭─╮╭─╮╭─╮╭─╮╭─╮╭─╮               ││
│ │   80%├─●─●─●─●─●─●─●─● Aug-v2 (79.8%)    ││
│ │      │╭─╮╭─╮╭─╮╭─╮                        ││
│ │   75%├─●─●─●─●─● Baseline (74.2%)        ││
│ │      │                                      ││
│ │   70%├──────────────────────────────────   ││
│ │      └─────────────────────────────────── →│
│ │        Epoch                               ││
│ └────────────────────────────────────────────┘│
│                                                │
│ Per-Class Performance:                         │
│ ┌────────────────────────────────────────────┐ │
│ │ Class        mAP    Precision  Recall      │ │
│ │ Personnel    0.89   0.92       0.87        │ │
│ │ Commodity    0.84   0.88       0.81        │ │
│ │ Action       0.78   0.85       0.74        │ │
│ │ Deity        0.81   0.83       0.80        │ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ Augmentation Impact:                           │
│ ┌────────────────────────────────────────────┐ │
│ │ Metric              Baseline  Augmented    │ │
│ │ mAP                 74.2%  →  82.3%  +10.9│ │
│ │ mAP@50              85.1%  →  90.2%  +6.0%│ │
│ │ mAP@75              72.5%  →  80.1%  +10.5│ │
│ │ Training Time       2h34m     3h12m  +18% │ │
│ │ Inference Speed     45 FPS    43 FPS   -4%│ │
│ └────────────────────────────────────────────┘ │
│                                                │
│ [Export Report] [Compare Models] [Share]      │
│                                                │
└────────────────────────────────────────────────┘
```

**Features**:
- 📈 Interactive training curves (with legend, zoom, hover)
- 🎯 Per-class performance breakdown
- 📊 Augmentation impact comparison
- 📋 Detailed metrics table
- 📥 Export as PDF/PNG/CSV
- 🔍 Drill-down into specific runs
- 🏆 Ranking and leaderboard of models

---

### 7. **Settings & Configuration** ⚙️
**Purpose**: System preferences, data management

**Layout**:
```
┌────────────────────────────────────────────────────┐
│ Settings                                           │
├────────────────────────────────────────────────────┤
│                                                    │
│ Display Settings:                                 │
│ ☑ Dark Mode                                       │
│ ☑ Animations                                      │
│ • Charts Theme: [Dark ▼]                          │
│                                                    │
│ Training Defaults:                                │
│ • Default Model: [Medium ▼]                       │
│ • Default Epochs: [50]                            │
│ • Default Batch Size: [16]                        │
│ • Default Device: [MPS ▼]                         │
│ ☑ Auto-enable Augmentation                        │
│                                                    │
│ Data Management:                                  │
│ • Data Directory: [/data]                         │
│ • Models Directory: [/models]                     │
│ • Cache Size: 12.3 GB / 50 GB                     │
│ [Clear Cache] [Manage Storage]                    │
│                                                    │
│ CDLI Integration:                                 │
│ • API Key: [••••••••••]                           │
│ • Auto-sync: ☑                                    │
│ • Sync Frequency: [Daily ▼]                       │
│                                                    │
│ Export & Sharing:                                 │
│ ☑ Include metadata in exports                     │
│ ☑ Anonymize researcher names                      │
│ • Default Export Format: [JSON ▼]                 │
│                                                    │
│ [Save] [Reset to Defaults]                        │
│                                                    │
└────────────────────────────────────────────────────┘
```

---

## 🎨 Visual Design & Animation Strategy

### Design Philosophy
- **Academic Elegance**: Clean, professional, trustworthy
- **Clarity First**: Never sacrifice clarity for decoration
- **Delightful Details**: Subtle animations that inform, not distract
- **Accessibility**: WCAG AA compliant, keyboard navigation
- **Dark Mode**: Soft on the eyes, professional appearance

### Color Palette
```
Primary Colors:
• Deep Blue (#1e3a8a) - Professional, trustworthy
• Amber (#d97706) - Highlights, warnings
• Emerald (#059669) - Success, validation

Grays:
• bg-gray-50, bg-gray-100, bg-gray-900
• text-gray-600, text-gray-800

Semantic:
• Success: #10b981 (green)
• Warning: #f59e0b (amber)
• Error: #ef4444 (red)
• Info: #3b82f6 (blue)
```

### Animation Principles
1. **Purpose**: Every animation should communicate information
2. **Speed**: 300-500ms for UI transitions, 1-2s for emphasis
3. **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)` for smooth feel
4. **Reduce Motion**: Respect `prefers-reduced-motion`

### Key Animations

#### **Training Progress** 
```
• Smooth line animation revealing mAP curve in real-time
• Pulsing metrics that light up when improving
• Gauge needles that smoothly swing to new values
```

#### **Model Comparison**
```
• Bar charts that slide in from left to right
• Badges that scale and appear when showing improvement
• Floating transitions between model details
```

#### **Tablet Gallery**
```
• Masonry grid layout with staggered fade-in
• Smooth lightbox modal transitions
• Soft image zoom on hover
• Smooth scrubbing through image sequences
```

#### **Status Indicators**
```
• Animated loading spinners (pulse, bounce)
• Progress bars with smooth animation
• Success checkmarks with bounce-in
• Error shake animations
```

---

## 🔄 Data Flow & WebSocket Integration

### Real-Time Progress Updates
```
Backend (Python):
  1. Pipeline step starts
  2. Emit WebSocket event: { step: "training", progress: 5 }
  3. Periodic updates every 100 batches: { progress: 15 }
  4. Step complete: { step: "training", progress: 100, success: true }

Frontend (React):
  1. Connect to WebSocket on mount
  2. Listen for progress events
  3. Update Zustand store
  4. UI components re-render with new data
  5. Animations triggered by state changes
```

### WebSocket Events
```python
{
  "event": "training_progress",
  "run_id": "train-001",
  "step": "training",
  "progress": 0-100,
  "epoch": 18,
  "batch": 145,
  "loss": 0.234,
  "mAP": 0.742,
  "eta_seconds": 5520,
  "gpu_memory": 78,
  "fps": 45
}
```

---

## 📁 Project Structure

```
cuneiform-translator/
├── web/
│   ├── frontend/
│   │   ├── public/
│   │   │   ├── logo.svg
│   │   │   ├── favicon.ico
│   │   │   └── og-image.png
│   │   ├── src/
│   │   │   ├── assets/
│   │   │   │   ├── icons/
│   │   │   │   └── images/
│   │   │   ├── components/
│   │   │   │   ├── Layout/
│   │   │   │   │   ├── Header.tsx
│   │   │   │   │   ├── Sidebar.tsx
│   │   │   │   │   └── Footer.tsx
│   │   │   │   ├── Charts/
│   │   │   │   │   ├── TrainingCurve.tsx
│   │   │   │   │   ├── ComparisonChart.tsx
│   │   │   │   │   └── MetricsGauge.tsx
│   │   │   │   ├── Gallery/
│   │   │   │   │   ├── TabletGallery.tsx
│   │   │   │   │   ├── ImageViewer.tsx
│   │   │   │   │   └── AnnotationOverlay.tsx
│   │   │   │   ├── Forms/
│   │   │   │   │   ├── TrainingConfig.tsx
│   │   │   │   │   ├── ImageUpload.tsx
│   │   │   │   │   └── SettingsPanel.tsx
│   │   │   │   └── Common/
│   │   │   │       ├── LoadingSpinner.tsx
│   │   │   │       ├── ProgressBar.tsx
│   │   │   │       ├── Card.tsx
│   │   │   │       └── Modal.tsx
│   │   │   ├── pages/
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── PipelineControl.tsx
│   │   │   │   ├── ModelGallery.tsx
│   │   │   │   ├── TabletLibrary.tsx
│   │   │   │   ├── DetectionInspector.tsx
│   │   │   │   ├── ResearchAnalytics.tsx
│   │   │   │   └── Settings.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useWebSocket.ts
│   │   │   │   ├── usePipelineAPI.ts
│   │   │   │   ├── useAnimation.ts
│   │   │   │   └── useLocalStorage.ts
│   │   │   ├── store/
│   │   │   │   ├── pipelineStore.ts
│   │   │   │   ├── modelStore.ts
│   │   │   │   └── uiStore.ts
│   │   │   ├── utils/
│   │   │   │   ├── api.ts
│   │   │   │   ├── formatters.ts
│   │   │   │   └── validators.ts
│   │   │   ├── styles/
│   │   │   │   ├── globals.css
│   │   │   │   ├── animations.css
│   │   │   │   └── tailwind.css
│   │   │   ├── App.tsx
│   │   │   └── main.tsx
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tsconfig.json
│   │   └── tailwind.config.js
│   └── backend/
│       ├── app.py (Flask app)
│       ├── config.py
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── pipeline.py
│       │   ├── models.py
│       │   ├── tablets.py
│       │   ├── metrics.py
│       │   └── websocket.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── orchestrator.py (calls run_complete_pipeline.py)
│       │   ├── model_manager.py
│       │   ├── storage.py
│       │   └── websocket_manager.py
│       ├── models/
│       │   └── database.py
│       ├── utils/
│       │   ├── decorators.py
│       │   ├── validators.py
│       │   └── formatters.py
│       └── requirements.txt
├── docker-compose.yml (for local dev)
├── docker/
│   ├── Dockerfile.frontend
│   └── Dockerfile.backend
└── docs/
    ├── API.md (endpoint documentation)
    ├── WEBSOCKET.md (real-time events)
    └── DEPLOYMENT.md (production setup)
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (3-4 days)
- [ ] Backend Flask app structure with CORS
- [ ] REST API endpoints for pipeline control
- [ ] Database schema for tracking runs
- [ ] Frontend project setup (Vite + React)
- [ ] Basic routing and layout components
- [ ] Authentication/authorization skeleton

**Deliverable**: Basic working app that lists tablets and can trigger training

### Phase 2: Real-time Monitoring (3-4 days)
- [ ] WebSocket integration (Flask-SocketIO)
- [ ] Background task processing (Celery)
- [ ] Progress streaming from orchestrator
- [ ] Real-time charts and metrics update
- [ ] Animated progress bars and spinners

**Deliverable**: Live training monitoring with animated progress

### Phase 3: Gallery & Visualization (3 days)
- [ ] Tablet gallery with photo album component
- [ ] Image viewer with annotation overlay
- [ ] Model comparison charts (Recharts)
- [ ] Detection result visualization
- [ ] Export functionality

**Deliverable**: Beautiful tablet browsing and model inspection

### Phase 4: Polish & Optimization (2-3 days)
- [ ] Animation refinement (Framer Motion)
- [ ] Dark mode implementation
- [ ] Responsive design fixes
- [ ] Performance optimization
- [ ] Accessibility audit (WCAG AA)
- [ ] Error handling and edge cases

**Deliverable**: Production-ready, beautiful interface

### Phase 5: Deployment & Documentation (2 days)
- [ ] Docker containerization
- [ ] Environment configuration
- [ ] API documentation
- [ ] Deployment guide
- [ ] User guide

**Deliverable**: Deployed web UI ready for researchers

---

## 💡 Advanced Features (Stretch Goals)

### Collaborative Research
- 👥 Multi-user sessions with real-time collaboration
- 💬 Comments and annotations on results
- 🔄 Shared models and experiment tracking

### Advanced Analytics
- 📊 Confusion matrix visualization
- 🎯 ROC/AUC curves
- 📈 Statistical significance testing
- 🔍 Error analysis dashboard

### Integration Features
- 🌐 CDLI API integration (automatic tablet sync)
- 📤 Hugging Face Model Hub integration (push models)
- 📊 Jupyter notebook export
- 🔗 Shareable result links

### AI-Assisted Features
- 🤖 Automated annotation suggestions
- 💡 Model recommendation engine
- 📝 Automatic report generation
- 🎯 Experiment proposal suggestions

---

## 🔒 Security Considerations

- API authentication (JWT tokens)
- CORS configuration for cross-origin requests
- Rate limiting on endpoints
- Input validation and sanitization
- File upload restrictions (size, type)
- Secure storage of model paths
- Audit logging of all operations

---

## 📊 Performance Targets

| Metric | Target |
|--------|--------|
| Page Load | < 2 seconds |
| Chart Render | < 500ms |
| Gallery Load (50 images) | < 1 second |
| API Response | < 200ms |
| WebSocket Latency | < 100ms |
| Lighthouse Score | > 90 |

---

## 🧪 Testing Strategy

### Unit Tests
```
Frontend:
- Components render correctly
- State updates work
- API calls are formatted correctly

Backend:
- API endpoints return correct data
- File operations work
- WebSocket events are sent properly
```

### Integration Tests
```
- Full training flow end-to-end
- File upload and processing
- Real-time updates via WebSocket
- Model comparison workflows
```

### E2E Tests (Cypress/Playwright)
```
- User can start training
- User can view results
- Gallery displays tablets
- Comparison works
- Export functions work
```

---

## 📝 Next Steps to Begin

1. **Review this plan** - Does this architecture align with your vision?
2. **Choose tech stack** - Confirm React + Flask + Recharts + Framer Motion?
3. **Set up backend structure** - Flask app, routes, WebSocket
4. **Create frontend skeleton** - Layout, routing, basic pages
5. **Build Phase 1** - Foundational working prototype

**Ready to start?** I can begin with Phase 1 immediately!

---

## Questions to Consider

1. **Authentication**: Should we support multiple users or single-user access?
2. **Storage**: Local only or cloud storage (S3) integration?
3. **Hosting**: Local deployment, Docker, cloud (AWS/GCP)?
4. **Customization**: Should researchers be able to create custom experiments?
5. **Export**: What formats matter most (PDF, CSV, JSON, PNG)?
6. **Real-time**: How important is live progress vs polling?

---

**This plan provides:**
✅ Clear architecture and tech stack
✅ 7 major pages with detailed mockups
✅ Animation and design principles
✅ Realistic implementation timeline (1-2 weeks)
✅ Foundation for scaling
✅ Security and performance considerations

**Shall we begin? 🚀**
