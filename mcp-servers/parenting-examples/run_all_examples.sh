#!/bin/bash

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         Parenting MCP Servers - Demo Suite                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

echo "Running all parenting examples..."
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  BABY TRACKER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 baby_tracker.py
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  SLEEP SCHEDULE HELPER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 sleep_schedule.py
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  QUICK PARENT HELPER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 parent_helper.py
echo ""

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✓ All demos complete!                                       ║"
echo "║                                                              ║"
echo "║  These tools help with:                                     ║"
echo "║  • Tracking feedings, diapers, sleep                        ║"
echo "║  • Calculating wake windows and bedtimes                    ║"
echo "║  • Quick conversions and safety checks                      ║"
echo "║  • Troubleshooting crying and milestones                    ║"
echo "║                                                              ║"
echo "║  Next: Integrate with Kiro CLI for voice queries!          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
