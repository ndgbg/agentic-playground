# Parenting MCP Servers

Practical MCP servers for parents with newborns. Because parenting is hard enough without doing mental math at 3am.

## 🍼 Baby Tracker

Track feedings, diapers, and sleep patterns.

**Tools:**
- `log_feeding` - Record breast/bottle/formula feeding
- `log_diaper` - Record diaper changes
- `get_last_feeding` - Check when baby last ate
- `get_daily_summary` - Today's feeding/diaper count
- `next_feeding_time` - Calculate when next feeding is due

**Example:**
```bash
python3 baby_tracker.py
```

**Use Cases:**
- "When did I last feed the baby?"
- "How many diapers today?"
- "When is the next feeding?"

---

## 😴 Sleep Schedule Helper

Optimize baby's sleep schedule based on age-appropriate wake windows.

**Tools:**
- `calculate_wake_windows` - Get wake windows for baby's age
- `suggest_bedtime` - Calculate bedtime based on last nap
- `log_sleep_session` - Track naps and night sleep
- `total_sleep_today` - Calculate total sleep hours
- `sleep_regression_check` - Check if in regression period

**Example:**
```bash
python3 sleep_schedule.py
```

**Use Cases:**
- "What's the right wake window for a 2-month-old?"
- "When should bedtime be if last nap ended at 4pm?"
- "Is my baby in a sleep regression?"

---

## 👶 Quick Parent Helper

Practical tools for exhausted parents.

**Tools:**
- `bottle_temp_check` - Check if bottle is safe temperature
- `formula_calculator` - Calculate formula amounts by weight
- `crying_checklist` - Troubleshooting checklist for crying
- `milestone_tracker` - Age-appropriate milestones
- `emergency_check` - Check if symptoms need immediate care
- `quick_conversion` - Convert oz/ml, lbs/kg, F/C

**Example:**
```bash
python3 parent_helper.py
```

**Use Cases:**
- "Is 98°F safe for a bottle?"
- "How much formula for a 10lb baby?"
- "Baby won't stop crying - what should I check?"
- "Convert 4oz to ml"

---

## Quick Start

Run any example:
```bash
cd parenting-examples
python3 baby_tracker.py
python3 sleep_schedule.py
python3 parent_helper.py
```

Or run all demos:
```bash
./run_all_examples.sh
```

---

## Real-World Scenarios

### Scenario 1: Middle of the Night
```
You: "When did I last feed the baby?"
Server: "Last feeding: bottle 2h 15m ago"

You: "When is next feeding due?"
Server: "Next feeding in 45m (around 3:30 AM)"
```

### Scenario 2: Nap Time Confusion
```
You: "Last nap ended at 2:30pm, when should bedtime be?"
Server: "Suggested bedtime: 4:00 PM (Based on 1.5 hour wake window)"

You: "What's the right wake window for 8 weeks?"
Server: "Age 8 weeks: Wake window: 60-90 minutes, Expected naps: 4"
```

### Scenario 3: Crying Baby
```
You: "Baby crying for 20 minutes, what should I check?"
Server: "Crying Checklist:
  🍼 Hungry? (Last feeding >2-3 hours ago?)
  💩 Diaper? (Check for wet/dirty)
  😴 Tired? (Awake >90 minutes?)
  🌡️ Temperature? (Too hot/cold?)
  🤗 Comfort? (Needs cuddles/rocking?)
  💨 Gas? (Try burping/bicycle legs)"
```

### Scenario 4: Formula Prep
```
You: "How much formula for 10lb baby?"
Server: "For 10 lbs baby:
  Daily: 25.0 oz
  Per feeding (6x/day): 4.2 oz"

You: "Is 102°F safe for bottle?"
Server: "Bottle temp: 102°F
  ⚠️ Slightly warm
  Let it cool for 30 seconds"
```

---

## Why These Are Useful

### At 3am When You're Exhausted
- No mental math required
- Quick answers to common questions
- Checklists when you can't think straight

### For First-Time Parents
- Age-appropriate guidance
- Milestone tracking
- Emergency symptom checking

### For Tracking Patterns
- Identify feeding schedules
- Optimize sleep routines
- Share data with pediatrician

---

## Extending for Your Needs

Add custom tools:

```python
def growth_tracker(args):
    # Track weight, height, head circumference
    pass

def vaccine_schedule(args):
    # Remind about upcoming vaccines
    pass

def doctor_visit_prep(args):
    # Compile questions for pediatrician
    pass
```

---

## Safety Note

⚠️ **These tools are helpers, not medical advice.**

- Always consult your pediatrician for medical concerns
- Trust your parental instincts
- When in doubt, call your doctor
- Emergency symptoms = call 911

---

## Tips for Sleep-Deprived Parents

1. **Use voice commands** - Integrate with Kiro CLI for hands-free
2. **Set up shortcuts** - Create aliases for common queries
3. **Share with partner** - Both parents can track together
4. **Export data** - Save logs for pediatrician visits
5. **Customize** - Adjust wake windows for your baby's needs

---

## Next Steps

1. Run the examples to see them in action
2. Modify for your baby's specific schedule
3. Add tools for your unique needs
4. Integrate with Kiro CLI for voice queries

---

**Remember:** You're doing great! These tools are here to help, not add stress. Use what's helpful, ignore what's not. 💙

---

*Created for exhausted parents everywhere*  
*No dependencies required - just Python 3*
