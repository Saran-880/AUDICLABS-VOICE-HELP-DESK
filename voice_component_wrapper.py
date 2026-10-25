
from pathlib import Path
import streamlit.components.v1 as components

_COMPONENT_DIR = Path(__file__).resolve().parent / "voice_component" / "frontend"

voice_component = components.declare_component(
    "audiclabs_voice_helpdesk",
    path=str(_COMPONENT_DIR),
)
