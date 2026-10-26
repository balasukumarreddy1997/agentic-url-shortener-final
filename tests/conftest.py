"""Test isolation: every path the app or orchestrator writes to points at a temp dir.

This runs before test modules are imported, which matters because app.main constructs
its store and workflow engine at import time.
"""

import atexit
import os
import shutil
import tempfile

_TMP = tempfile.mkdtemp(prefix="agentic-tests-")
os.environ["DATABASE_PATH"] = os.path.join(_TMP, "urls.db")
os.environ["WORKFLOW_DB_PATH"] = os.path.join(_TMP, "workflows.db")
os.environ["AGENTIC_ARTIFACTS_DIR"] = os.path.join(_TMP, "artifacts")
os.environ.pop("ALLOW_DEMO_AUTO_APPROVE", None)
atexit.register(shutil.rmtree, _TMP, ignore_errors=True)
