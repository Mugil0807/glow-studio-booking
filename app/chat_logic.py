import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.config import get_config, SYSTEM_PROMPT
from app.rag_pipeline import ingest_pdfs, retrieve_context
from app.tools import parse_booking_json, process_confirmed_booking
from models.llm import get_llm

def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "booking_pending" not in st.session_state:
        st.session_state.booking_pending = None

def get_llm_response(user_input):
    cfg = get_config()
    llm = get_llm()
    vs  = st.session_state.vectorstore

    # RAG context
    rag_context = retrieve_context(vs, user_input) if vs else ""
    system_content = SYSTEM_PROMPT
    if rag_context:
        system_content += f"\n\n--- RETRIEVED CONTEXT ---\n{rag_context}"

    # Build message history (last MAX_HISTORY messages)
    history = st.session_state.messages[-(cfg["MAX_HISTORY"]):]
    formatted = [SystemMessage(content=system_content)]
    for m in history:
        if m["role"] == "user":
            formatted.append(HumanMessage(content=m["content"]))
        else:
            formatted.append(AIMessage(content=m["content"]))
    formatted.append(HumanMessage(content=user_input))

    response = llm.invoke(formatted)
    return response.content

def chat_page():
    init_session()

    st.markdown("""
    <div style='padding: 2rem 0 1rem 0;'>
        <h1 style='font-family: Cormorant Garamond, serif; font-size: 2.8rem; font-weight: 300; color: #2C2C2C; margin: 0;'>
            Book Your Experience
        </h1>
        <p style='color: #8A7F7A; font-size: 0.9rem; margin-top: 0.5rem; letter-spacing: 0.05em;'>
            Chat with our AI assistant · Ask questions · Book appointments
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("**📎 Upload Service Menu / Brochure**")
        uploaded_files = st.file_uploader(
            "Upload PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        if uploaded_files:
            if st.button("Process PDFs", use_container_width=True):
                with st.spinner("Reading and indexing PDFs..."):
                    vs = ingest_pdfs(uploaded_files)
                    if vs:
                        st.session_state.vectorstore = vs
                        st.success(f"✓ {len(uploaded_files)} PDF(s) indexed")
                    else:
                        st.error("Could not extract text from PDFs.")

        if st.session_state.vectorstore:
            st.markdown("""
            <div style='background: #F0EDE8; border-radius: 4px; padding: 0.8rem 1rem; margin-top: 0.5rem; font-size: 0.8rem; color: #5C5C5C;'>
            ✅ PDF knowledge active — I can answer questions about your documents.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown("**Our Services**")
        from app.config import SERVICES
        for s in SERVICES:
            st.markdown(f"<div style='font-size: 0.82rem; color: #5C5C5C; padding: 3px 0;'>· {s}</div>", unsafe_allow_html=True)

    with col1:
        # Display chat history
        chat_container = st.container()
        with chat_container:
            if not st.session_state.messages:
                st.markdown("""
                <div style='background: white; border: 1px solid #EDE8E3; border-radius: 4px; padding: 2rem; text-align: center; color: #8A7F7A; margin-bottom: 1rem;'>
                    <div style='font-family: Cormorant Garamond, serif; font-size: 1.3rem; color: #2C2C2C; margin-bottom: 0.5rem;'>Welcome to Glow Studio ✨</div>
                    <div style='font-size: 0.85rem;'>Ask me about our services, pricing, or say <em>"I'd like to book an appointment"</em> to get started.</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                for msg in st.session_state.messages:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])

        # Pending booking confirmation banner
        if st.session_state.booking_pending:
            data = st.session_state.booking_pending
            st.markdown(f"""
            <div style='background: #FFF8F6; border: 1px solid #E8C4B8; border-radius: 4px; padding: 1.2rem 1.5rem; margin: 1rem 0;'>
                <div style='font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase; color: #C4736A; margin-bottom: 0.8rem;'>Booking Summary</div>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem 1.5rem; font-size: 0.87rem;'>
                    <div><span style='color:#8A7F7A;'>Name: </span><strong>{data.get('customer_name','')}</strong></div>
                    <div><span style='color:#8A7F7A;'>Service: </span><strong>{data.get('service_type','')}</strong></div>
                    <div><span style='color:#8A7F7A;'>Email: </span><strong>{data.get('customer_email','')}</strong></div>
                    <div><span style='color:#8A7F7A;'>Date: </span><strong>{data.get('preferred_date','')}</strong></div>
                    <div><span style='color:#8A7F7A;'>Phone: </span><strong>{data.get('customer_phone','')}</strong></div>
                    <div><span style='color:#8A7F7A;'>Time: </span><strong>{data.get('preferred_time','')}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            bc1, bc2 = st.columns(2)
            with bc1:
                if st.button("✓ Confirm Booking", use_container_width=True):
                    with st.spinner("Saving your booking..."):
                        booking_id, email_ok, email_msg = process_confirmed_booking(data)
                    if booking_id:
                        confirm_msg = f"🎉 **Booking confirmed!** Your ID is `{booking_id}`."
                        if email_ok:
                            confirm_msg += " A confirmation email has been sent to you."
                        else:
                            confirm_msg += f" _(Email note: {email_msg})_"
                        st.session_state.messages.append({"role": "assistant", "content": confirm_msg})
                        st.session_state.booking_pending = None
                        st.success(f"Booking saved! ID: {booking_id}")
                        st.rerun()
                    else:
                        st.error(f"Could not save booking: {email_msg}")
            with bc2:
                if st.button("✗ Cancel", use_container_width=True):
                    st.session_state.booking_pending = None
                    st.session_state.messages.append({"role": "assistant", "content": "No problem — booking cancelled. Let me know if you'd like to start over or change anything."})
                    st.rerun()

        # Chat input
        user_input = st.chat_input("Ask about our services or say 'I'd like to book'...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner(""):
                try:
                    response = get_llm_response(user_input)
                except ValueError as e:
                    response = f"⚠️ Configuration issue: {str(e)}. Please add your GROQ_API_KEY to `.streamlit/secrets.toml`."
                except Exception as e:
                    response = f"Sorry, I encountered an error: {str(e)}"

            # Check if LLM signalled a confirmed booking
            if "BOOKING_CONFIRMED" in response:
                booking_data = parse_booking_json(response)
                if booking_data:
                    st.session_state.booking_pending = booking_data
                    clean_response = response.split("BOOKING_CONFIRMED")[0].strip()
                    clean_response += "\n\nPlease review the booking summary below and confirm."
                    response = clean_response

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
