import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import io

st.title("Multi-Feature AI App")

api_key = st.text_input("Enter your Gemini API Key:", type="password")

if api_key:
    client = genai.Client(api_key=api_key)

    def generate_response(prompt, temperature=0.3):
        try:
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
            config_params = types.GenerateContentConfig(temperature=temperature)
            response = client.models.generate_content(
                model="gemini-2.0-flash", contents=contents, config=config_params
            )
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_math_response(prompt, temperature=0.1):
        system_prompt = "You are a Math Mastermind. Explain step by step and solve accurately."
        full_prompt = f"{system_prompt}\n\nMath Problem: {prompt}"
        return generate_response(full_prompt, temperature)

    def generate_image(prompt):
        banned_words = ["violence", "nudity", "drugs"]
        if any(word in prompt.lower() for word in banned_words):
            return None, "Unsafe prompt detected!"
        try:
            contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
            config_params = types.GenerateContentConfig(temperature=0.5)
            response = client.models.generate_content(
                model="gemini-2.5-flash-image", contents=contents, config=config_params
            )
            image_bytes = response.image_bytes
            img = Image.open(BytesIO(image_bytes))
            return img, None
        except Exception as e:
            return None, f"Error: {str(e)}"

    def run_ai_teaching_assistant():
        st.header("AI Teaching Assistant")
        st.write("Ask anything and get insightful answers.")
        if "history_ata" not in st.session_state:
            st.session_state.history_ata = []

        col_clear, col_export = st.columns([1, 2])
        with col_clear:
            if st.button("Clear Conversation", key="clear_ata"):
                st.session_state.history_ata = []
        with col_export:
            if st.session_state.history_ata:
                export_text = "".join(
                    f"Q{i+1}: {qa['question']}\nA{i+1}: {qa['answer']}\n\n"
                    for i, qa in enumerate(st.session_state.history_ata)
                )
                bio = io.BytesIO()
                bio.write(export_text.encode("utf-8"))
                bio.seek(0)
                st.download_button("Export Chat History", data=bio, file_name="AI_Teaching_Assistant.txt", mime="text/plain")

        user_input = st.text_input("Enter your question here:", key="input_ata")
        if st.button("Ask", key="ask_ata"):
            if user_input.strip():
                with st.spinner("Generating AI response..."):
                    response = generate_response(user_input.strip(), temperature=0.3)
                st.session_state.history_ata.append({"question": user_input.strip(), "answer": response})
                st.rerun()
            else:
                st.warning("Please enter a question before clicking Ask.")

        st.markdown("### Conversation History")
        for idx, qa in enumerate(st.session_state.history_ata, start=1):
            st.markdown(f"**Q{idx}:** {qa['question']}")
            st.markdown(f"**A{idx}:** {qa['answer']}")

    def run_math_mastermind():
        st.header("Math Mastermind")
        st.write("Solve math problems step by step.")
        if "history_mm" not in st.session_state:
            st.session_state.history_mm = []

        user_input = st.text_input("Enter math problem:", key="input_mm")
        if st.button("Solve", key="solve_mm"):
            if user_input.strip():
                with st.spinner("Solving..."):
                    response = generate_math_response(user_input.strip())
                st.session_state.history_mm.append({"problem": user_input.strip(), "solution": response})
                st.rerun()
            else:
                st.warning("Enter a problem first.")

        st.markdown("### Problem History")
        for idx, qa in enumerate(st.session_state.history_mm, start=1):
            st.markdown(f"**Problem {idx}:** {qa['problem']}")
            st.markdown(f"**Solution {idx}:** {qa['solution']}")

    def run_safe_ai_image_generator():
        st.header("Safe AI Image Generator")
        st.write("Generate safe images using AI.")
        if "history_img" not in st.session_state:
            st.session_state.history_img = []

        prompt = st.text_input("Enter image description:", key="input_img")
        if st.button("Generate", key="gen_img"):
            if prompt.strip():
                with st.spinner("Generating image..."):
                    img, error = generate_image(prompt.strip())
                    if error:
                        st.warning(error)
                    else:
                        st.image(img)
                        st.session_state.history_img.append({"prompt": prompt, "image": img})
            else:
                st.warning("Enter a description first.")

    st.sidebar.title("Select Tool")
    choice = st.sidebar.selectbox("Choose feature:", ["Teaching Assistant", "Math Mastermind", "Safe AI Image Generator"])

    if choice == "Teaching Assistant":
        run_ai_teaching_assistant()
    elif choice == "Math Mastermind":
        run_math_mastermind()
    elif choice == "Safe AI Image Generator":
        run_safe_ai_image_generator()
else:
    st.warning("Enter your Gemini API Key to use the app.")
    
st.divider()
st.write("Goodbye, Codingal! 🥲")
