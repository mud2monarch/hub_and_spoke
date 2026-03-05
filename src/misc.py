import matplotlib.font_manager as fm

print(sorted(set(f.name for f in fm.fontManager.ttflist)))
