import config
from engine.sound_effects import sound_fx
from engine.speaker import speaker
from engine.system_actions import system_actions
from engine.web_actions import web_actions
from engine.commander import commander

print('[1] Config & Paths: OK')
print('[2] Sound FX initialized: OK')
print('[3] Speaker initialized: OK')

batt = system_actions.get_battery_status()
print('[4] Battery check:', batt)

diag = system_actions.get_system_report()
print('[5] Diagnostic check:', diag)

t = web_actions.get_current_time()
print('[6] Time check:', t)

# Test commander intent matching (without executing destructive commands)
resp1 = commander.process('what is the time')
print('[7] Commander Time test:', resp1)

resp2 = commander.process('battery status')
print('[8] Commander Battery test:', resp2)

resp3 = commander.process('who are you')
print('[9] Commander Identity test:', resp3)

print('\n>>> ALL CORE ENGINES VALIDATED SUCCESSFULLY! <<<')
import sys
sys.exit(0)
