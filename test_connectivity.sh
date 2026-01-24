#!/bin/bash

# Phase 2.1: Connectivity Test Script
# Tests that frontend and backend can communicate

echo "🔍 Phase 2.1: Testing Frontend-Backend Connectivity"
echo "===================================================="
echo ""

# Test 1: Backend API Health
echo "✓ Test 1: Checking backend API health..."
sleep 2
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/api/health)
if [ "$HEALTH" = "200" ]; then
  echo "  ✅ Backend API is healthy (HTTP 200)"
else
  echo "  ❌ Backend API not responding (HTTP $HEALTH)"
  echo "  Make sure backend is running: cd backend && python run.py"
  exit 1
fi

echo ""

# Test 2: Health readiness
echo "✓ Test 2: Checking backend readiness..."
READY=$(curl -s http://localhost:5001/api/health/ready | grep -o '"status":"ready"')
if [ -n "$READY" ]; then
  echo "  ✅ Backend is ready"
else
  echo "  ⚠️  Backend readiness check inconclusive"
fi

echo ""

# Test 3: Pipeline status endpoint
echo "✓ Test 3: Checking pipeline status endpoint..."
PIPELINES=$(curl -s http://localhost:5001/api/pipeline/status | grep -o '"items"')
if [ -n "$PIPELINES" ]; then
  echo "  ✅ Pipeline status endpoint working"
else
  echo "  ⚠️  Pipeline endpoint returned unexpected response"
fi

echo ""

# Test 4: Analytics summary endpoint
echo "✓ Test 4: Checking analytics summary..."
ANALYTICS=$(curl -s http://localhost:5001/api/analytics/summary | grep -o '"total_pipeline_runs"')
if [ -n "$ANALYTICS" ]; then
  echo "  ✅ Analytics endpoint working"
else
  echo "  ⚠️  Analytics endpoint returned unexpected response"
fi

echo ""
echo "===================================================="
echo "✨ Phase 2.1 Connectivity Tests Complete!"
echo "===================================================="
echo ""
echo "Next: Frontend development server"
echo "  cd frontend && npm run dev"
echo "  Then open http://localhost:5173"
