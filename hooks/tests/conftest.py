import os
import sys

# Permite `import tdd_common` etc. ao rodar pytest de qualquer cwd.
HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)
