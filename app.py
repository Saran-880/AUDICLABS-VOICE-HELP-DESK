import streamlit as st

from scripts.rag import answer_question
from backend import (
    AudicLabsError,
    create_ticket,
    check_health,
    get_stt_languages,
    get_stt_models,
    get_tts_voices,
    get_tts_languages,
)
from voice_component_wrapper import voice_component


st.set_page_config(
    page_title="AudicLabs Voice Help Desk",
    page_icon="🎙️",
    layout="centered",
)

st.title("🎙️ AudicLabs Help Desk")
st.caption(
    "Ask questions about AudicLabs documentation by typing or speaking."
)


# -------------------- Session state --------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_args" not in st.session_state:
    st.session_state.voice_args = {
        "stt_ticket": None,
        "voice_answer": None,
        "tts_ticket": None,
        "voice_active": False,
    }

if "last_voice_event_id" not in st.session_state:
    st.session_state.last_voice_event_id = None

if "api_health_result" not in st.session_state:
    st.session_state.api_health_result = None

if "voice_options_result" not in st.session_state:
    st.session_state.voice_options_result = None


# -------------------- API diagnostics --------------------

with st.sidebar:
    st.header("API diagnostics")

    if st.button("Check API health", use_container_width=True):
        try:
            with st.spinner("Checking API health..."):
                st.session_state.api_health_result = check_health()
        except AudicLabsError as exc:
            st.session_state.api_health_result = {"error": str(exc)}

    if st.session_state.api_health_result is not None:
        st.caption("Health check response")
        st.json(st.session_state.api_health_result)

    st.divider()
    st.subheader("Speech options")

    if st.button("Load available options", use_container_width=True):
        results = {}
        errors = {}

        lookup_functions = {
            "STT languages": get_stt_languages,
            "STT models": get_stt_models,
            "TTS voices": get_tts_voices,
            "TTS languages": get_tts_languages,
        }

        progress = st.progress(0)

        for index, (name, function) in enumerate(
            lookup_functions.items(), start=1
        ):
            try:
                results[name] = function()
            except AudicLabsError as exc:
                errors[name] = str(exc)

            progress.progress(index / len(lookup_functions))

        st.session_state.voice_options_result = {
            "results": results,
            "errors": errors,
        }

    if st.session_state.voice_options_result is not None:
        lookup_data = st.session_state.voice_options_result

        for name, data in lookup_data["results"].items():
            with st.expander(name):
                st.json(data)

        for name, error in lookup_data["errors"].items():
            st.warning(f"{name}: {error}")


# -------------------- Parse runtime options --------------------

lookup_results = (
    st.session_state.voice_options_result or {}
).get("results", {})


def get_data_items(response):
    """Return the data list from a lookup response."""
    if not isinstance(response, dict):
        return []

    items = response.get("data", [])

    if isinstance(items, list):
        return items

    return []


# STT languages returned by the API.
stt_languages = get_data_items(
    lookup_results.get("STT languages", {})
)

stt_language_options = {}
for item in stt_languages:
    if not isinstance(item, dict):
        continue

    code = item.get("code")
    name = item.get("name", code)
    enabled = item.get("enabled", True)

    if code and enabled:
        stt_language_options[code] = name

# Keep automatic detection available when provided by the API.
if "auto" not in stt_language_options:
    stt_language_options["auto"] = "Automatic detection"

# TTS voices returned by the API.
tts_voices = get_data_items(
    lookup_results.get("TTS voices", {})
)

tts_voice_options = {}
for item in tts_voices:
    if not isinstance(item, dict):
        continue

    voice_id = item.get("voice_id")
    name = item.get("name", voice_id)
    language = item.get("language")

    if voice_id:
        label = f"{name} ({language})" if language else name
        tts_voice_options[voice_id] = label

# Fallback to a voice ID confirmed by the API lookup.
# The selection will use live API results when they are available.
if not tts_voice_options:
    tts_voice_options["voice_bilal_en"] = "Bilal (fallback)"

stt_codes = list(stt_language_options.keys())
tts_voice_ids = list(tts_voice_options.keys())

if "selected_stt_language" not in st.session_state:
    st.session_state.selected_stt_language = (
        "auto" if "auto" in stt_codes else stt_codes[0]
    )

if st.session_state.selected_stt_language not in stt_codes:
    st.session_state.selected_stt_language = (
        "auto" if "auto" in stt_codes else stt_codes[0]
    )

if "selected_tts_voice" not in st.session_state:
    st.session_state.selected_tts_voice = tts_voice_ids[0]

if st.session_state.selected_tts_voice not in tts_voice_ids:
    st.session_state.selected_tts_voice = tts_voice_ids[0]


# -------------------- Voice settings --------------------

with st.sidebar:
    st.divider()
    st.subheader("Voice settings")

    selected_stt_language = st.selectbox(
        "Speech recognition language",
        options=stt_codes,
        format_func=lambda code: (
            f"{stt_language_options.get(code, code)} — {code}"
        ),
        key="selected_stt_language",
        help="Load available options to retrieve supported languages.",
    )

    selected_tts_voice = st.selectbox(
        "Spoken answer voice",
        options=tts_voice_ids,
        format_func=lambda voice_id: (
            f"{tts_voice_options.get(voice_id, voice_id)} — {voice_id}"
        ),
        key="selected_tts_voice",
        help="Load available options to retrieve supported voices.",
    )


# -------------------- Question processing --------------------

def process_question(question):
    question = question.strip()

    if not question:
        return

    # Stop any previous voice operation before handling a new question.
    st.session_state.voice_args.update({
        "voice_answer": None,
        "tts_ticket": None,
        "stt_ticket": None,
        "voice_active": False,
    })

    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    history = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in st.session_state.messages[:-1]
    )

    try:
        with st.spinner("Searching the documentation..."):
            result = answer_question(
                question,
                history=history,
            )

        answer = result.get(
            "answer",
            "I couldn't find sufficient information in the AudicLabs documentation.",
        )
        sources = result.get("sources", [])

    except Exception:
        answer = (
            "Sorry, I couldn't process your question. "
            "Please try again."
        )
        sources = []
        st.error(
            "Question processing failed. Check the terminal for details."
        )

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })

    # Create a TTS ticket only when a text answer is available.
    if not answer.startswith("Sorry, I couldn't process your question."):
        try:
            ticket_info = create_ticket("tts")

            st.session_state.voice_args["voice_answer"] = answer
            st.session_state.voice_args["tts_ticket"] = ticket_info

        except AudicLabsError as exc:
            st.session_state.voice_args["voice_answer"] = None
            st.session_state.voice_args["tts_ticket"] = None

            st.warning(
                "Your text answer is ready, but speech generation "
                f"could not start: {exc}"
            )


# -------------------- Display conversation --------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            for source in message.get("sources", []):
                title = source.get("title", "Documentation source")
                url = source.get("url")

                if url:
                    st.markdown(f"- [{title}]({url})")


# -------------------- Voice component --------------------

event = voice_component(
    **st.session_state.voice_args,
    stt_language=st.session_state.selected_stt_language,
    tts_voice=st.session_state.selected_tts_voice,
    key="audiclabs_voice",
    default=None,
)

if isinstance(event, dict):
    event_id = event.get("event_id")
    action = event.get("action")

    is_new_event = (
        event_id is not None
        and event_id != st.session_state.last_voice_event_id
    )

    if is_new_event:
        st.session_state.last_voice_event_id = event_id

        if action == "request_stt_ticket":
            try:
                # Create a fresh single-use ticket for each recording.
                st.session_state.voice_args["stt_ticket"] = (
                    create_ticket("stt")
                )
                st.session_state.voice_args["voice_active"] = True
                st.rerun()

            except AudicLabsError as exc:
                st.session_state.voice_args["stt_ticket"] = None
                st.session_state.voice_args["voice_active"] = False
                st.error(
                    f"Could not start speech recognition: {exc}"
                )

        elif action == "question":
            spoken_question = event.get("text", "").strip()

            if spoken_question:
                process_question(spoken_question)
                st.rerun()
            else:
                st.warning(
                    "No recognized question was received. "
                    "Please try speaking again."
                )

        elif action == "stop":
            st.session_state.voice_args["stt_ticket"] = None
            st.session_state.voice_args["voice_active"] = False
            st.rerun()


# -------------------- Typed questions --------------------

typed_question = st.chat_input(
    "Or type a question about AudicLabs..."
)

if typed_question:
    process_question(typed_question)
    st.rerun()