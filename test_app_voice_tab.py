# -*- coding: utf-8 -*-
import sys
import os
import pytest

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


@pytest.mark.skip(reason="Streamlit AppTest has known format_func protobuf limitation on rerun")
def test_app_voice_tab():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(os.path.abspath("app.py"), default_timeout=60)
    at.run()
    assert len(at.exception) == 0, f"Exceptions on init: {[e.message for e in at.exception]}"


if __name__ == "__main__":
    from streamlit.testing.v1 import AppTest
    print("Initializing AppTest...")
    at = AppTest.from_file(os.path.abspath("app.py"), default_timeout=60)
    at.run()
    print(f"Exceptions on initial load: {len(at.exception)}")
    assert len(at.exception) == 0, f"Exceptions on init: {[e.message for e in at.exception]}"
    print("SUCCESS: App loaded without ANY exception!")
