with open('app/map_renderer.py', 'r', encoding='utf-8') as f: lines = f.readlines()
with open('app/map_renderer.py', 'w', encoding='utf-8') as f:
    for line in lines:
        if 'btnClusterToggle' in line or 'btnSim' in line:
            continue
        f.write(line)

