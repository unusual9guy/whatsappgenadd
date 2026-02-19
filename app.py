"""
WhatsApp Ad Creative Generator
Generates professional product ad creatives using Gemini 3 Pro Image (Nano Banana Pro).
"""

import io
import os
import base64
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# ──────────────────────────────────────────────
#  Page config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Ad Creative Generator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
#  Custom CSS — premium dark theme
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* ── Import font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Root variables ── */
:root {
    --gold: #D4A853;
    --gold-light: #E8C97A;
    --dark-bg: #0E1117;
    --card-bg: #1A1D26;
    --card-border: #2A2D38;
    --text-primary: #F0F2F6;
    --text-secondary: #9CA3AF;
    --accent-gradient: linear-gradient(135deg, #D4A853 0%, #F0D78C 50%, #D4A853 100%);
}

/* ── Global ── */
.stApp { font-family: 'Inter', sans-serif; }

/* ── Header ── */
.hero-header {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
    margin-bottom: 1.5rem;
}
.hero-header h1 {
    font-size: 2.4rem;
    font-weight: 700;
    background: var(--accent-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: .4rem;
}
.hero-header p {
    color: var(--text-secondary);
    font-size: 1.05rem;
    font-weight: 300;
}

/* ── Upload cards ── */
.upload-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: border-color .25s, box-shadow .25s;
}
.upload-card:hover {
    border-color: var(--gold);
    box-shadow: 0 0 20px rgba(212,168,83,.12);
}
.upload-card h3 {
    color: var(--gold-light);
    font-weight: 600;
    margin-bottom: .3rem;
    font-size: 1.1rem;
}
.upload-card p {
    color: var(--text-secondary);
    font-size: .85rem;
}

/* ── Generate button ── */
div.stButton > button {
    background: var(--accent-gradient) !important;
    color: #1A1D26 !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: .85rem 2.5rem !important;
    letter-spacing: .5px;
    transition: transform .15s, box-shadow .15s !important;
}
div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(212,168,83,.35) !important;
}

/* ── Result card ── */
.result-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-top: 1rem;
}
.result-card h2 {
    color: var(--gold-light);
    font-weight: 600;
    font-size: 1.3rem;
    margin-bottom: 1rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--card-bg);
    border-right: 1px solid var(--card-border);
}
section[data-testid="stSidebar"] .stMarkdown h2 {
    color: var(--gold-light);
    font-size: 1.15rem;
}

/* ── Status ── */
.status-badge {
    display: inline-block;
    padding: .3rem .8rem;
    border-radius: 999px;
    font-size: .8rem;
    font-weight: 500;
}
.status-ready { background: #1a3a2a; color: #4ade80; }
.status-warn  { background: #3a2a1a; color: #fbbf24; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    api_key = os.getenv("GOOGLE_API_KEY", "")
    if api_key:
        st.markdown(
            '<span class="status-badge status-ready">● API Key Loaded</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-badge status-warn">⚠ API Key Missing</span>',
            unsafe_allow_html=True,
        )
        st.caption("Set `GOOGLE_API_KEY` in your `.env` file")

    st.markdown("---")
    st.markdown("### 🖼️ Output Settings")

    aspect_ratio = st.selectbox(
        "Aspect Ratio",
        options=["4:5", "1:1", "3:4", "9:16", "16:9", "3:2", "2:3"],
        index=0,
        help="4:5 is ideal for Instagram / WhatsApp ads",
    )

    image_size = st.selectbox(
        "Resolution",
        options=["1K", "2K"],
        index=1,
        help="2K provides higher quality output",
    )

    st.markdown("---")
    st.markdown("### 📋 Model Info")
    st.markdown(
        '<span class="status-badge status-ready">● gemini-3-pro-image-preview</span>',
        unsafe_allow_html=True,
    )
    st.caption("Nano Banana Pro — best for professional ad creatives with complex compositions")


# ──────────────────────────────────────────────
#  Header
# ──────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>✨ Ad Creative Generator</h1>
    <p>Transform your product photos into premium, professional ad creatives — powered by Gemini AI</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  Inputs — three columns
# ──────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 1, 1], gap="large")

with col1:
    st.markdown("""
    <div class="upload-card">
        <h3>📦 Product Image</h3>
        <p>Upload a clear photo of your product</p>
    </div>
    """, unsafe_allow_html=True)
    product_file = st.file_uploader(
        "Upload Product Image",
        type=["jpg", "jpeg", "png", "webp"],
        key="product",
        label_visibility="collapsed",
    )
    if product_file:
        product_img = Image.open(product_file)
        st.image(product_img, caption="Product Image", width='stretch')

with col2:
    st.markdown("""
    <div class="upload-card">
        <h3>🏷️ Company Logo</h3>
        <p>Upload your company / brand logo</p>
    </div>
    """, unsafe_allow_html=True)
    logo_file = st.file_uploader(
        "Upload Company Logo",
        type=["jpg", "jpeg", "png", "webp"],
        key="logo",
        label_visibility="collapsed",
    )
    if logo_file:
        logo_img = Image.open(logo_file)
        st.image(logo_img, caption="Company Logo", width='stretch')

with col3:
    st.markdown("""
    <div class="upload-card">
        <h3>✏️ Product Name</h3>
        <p>Enter the name of your product</p>
    </div>
    """, unsafe_allow_html=True)
    product_name = st.text_input(
        "Product Name",
        placeholder="e.g. Tanjore Chowki",
        label_visibility="collapsed",
    )
    if product_name:
        st.success(f"Product: **{product_name}**")


# ──────────────────────────────────────────────
#  Prompt builder
# ──────────────────────────────────────────────
def build_prompt(product_name: str) -> str:
    """Build a refined, professional prompt for ad creative generation."""
    return f"""You are a world-class advertising creative director and luxury product photographer.

I am providing you with TWO reference images:
1. **Image 1** — The product photograph (the item to feature in the ad)
2. **Image 2** — The company logo (to be placed at the top of the composition)

Your task is to create a single, seamless, hyper-realistic, professional advertising image that looks like a premium magazine-quality product photoshoot.

### CRITICAL — Natural Product Placement:
- Do NOT simply cut-and-paste or overlay the product onto the background. You MUST re-render and re-light the product so it looks like it was **actually photographed in this scene**.
- Place the product at a **natural 3/4 perspective angle** — slightly tilted, as if resting naturally on the surface. NEVER place it flat or perfectly straight-on.
- The product must **interact realistically with the surface** — cast authentic soft shadows underneath and to one side, show subtle reflections on the surface beneath it, and match the scene's lighting direction.
- The product should look like someone carefully placed it on a real surface and a photographer took a beautiful shot of it.

### Composition & Layout (top to bottom, ONE continuous image):
- **Top**: Place the company logo prominently and naturally at the top of the image, centered.
- **Below the logo**: Render the text '+91 9007706401 / +91 9875691517' in an elegant gold serif typeface, slightly smaller than the logo.
- **Center**: Feature the product ("{product_name}") as the hero of the composition, placed at a natural angle on the surface. The product must be rendered with **razor-sharp detail and crisp edges** — preserve every texture, material finish, and fine detail from the original photo.
- **Bottom**: Render the product name "{product_name}" in an italic, elegant gold serif typeface at a **small, subtle size** — it should be noticeably smaller than the contact info text, acting as a discreet caption rather than a headline.

### Background & Surface (IMPORTANT):
- Use a **warm, premium marble or natural stone surface** as the base — think polished Italian marble with soft beige, cream, and warm golden-brown veins
- The surface should have a subtle sheen/polish that catches the light naturally
- The background should feel warm and inviting, NOT cold or dark — warm tones throughout
- The marble surface should extend seamlessly from foreground to background with natural perspective
- NO solid color backgrounds, NO dark/black backgrounds — always a textured premium surface

### Artistic Direction:
- Warm, golden ambient studio lighting — soft directional light from the upper left creating gentle highlights
- Minimal yet opulent aesthetic — no clutter, every element has breathing room
- All elements exist on the same continuous background — absolutely NO visible seams, borders, or section dividers
- The overall feel should be that of a high-end luxury Indian craft brand advertisement

### Product Clarity (CRITICAL):
- The product MUST appear **tack-sharp, high-definition, and crystal clear** — no blur, haze, or softness
- Preserve all original textures, grain, patterns, engravings, and material finishes from the reference photo
- Use focused studio-style lighting on the product to enhance sharpness and bring out fine details
- The product should look like it was photographed with a high-end macro lens at peak sharpness

Generate the final image now."""


# ──────────────────────────────────────────────
#  Generate button
# ──────────────────────────────────────────────
st.markdown("")  # spacing
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    generate = st.button("✨  Generate Ad Creative", width='stretch')

if generate:
    # ── Validation ──
    errors = []
    if not api_key:
        errors.append("Please enter your **Google API Key** in the sidebar.")
    if not product_file:
        errors.append("Please upload a **Product Image**.")
    if not logo_file:
        errors.append("Please upload a **Company Logo**.")
    if not product_name:
        errors.append("Please enter a **Product Name**.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        # ── Build inputs ──
        prompt_text = build_prompt(product_name)

        # Read raw file bytes and determine MIME types
        product_file.seek(0)
        logo_file.seek(0)
        product_bytes = product_file.read()
        logo_bytes = logo_file.read()

        # Map extensions to MIME types
        def get_mime(filename: str) -> str:
            ext = filename.rsplit(".", 1)[-1].lower()
            return {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "png": "image/png", "webp": "image/webp"}.get(ext, "image/png")

        product_part = types.Part(
            inline_data=types.Blob(
                mime_type=get_mime(product_file.name),
                data=product_bytes,
            )
        )
        logo_part = types.Part(
            inline_data=types.Blob(
                mime_type=get_mime(logo_file.name),
                data=logo_bytes,
            )
        )

        # ── Call Gemini ──
        with st.spinner("🎨  Generating your premium ad creative… This may take 30-60 seconds."):
            try:
                client = genai.Client(api_key=api_key)

                response = client.models.generate_content(
                    model="gemini-3-pro-image-preview",
                    contents=[prompt_text, product_part, logo_part],
                    config=types.GenerateContentConfig(
                        response_modalities=["TEXT", "IMAGE"],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                            image_size=image_size,
                        ),
                    ),
                )

                # ── Process response ──
                generated_image = None
                response_text = ""

                for part in response.candidates[0].content.parts:
                    if part.text is not None:
                        response_text += part.text
                    elif part.inline_data is not None:
                        # Build PIL image from raw bytes (avoids .format issues)
                        img_bytes = part.inline_data.data
                        generated_image = Image.open(io.BytesIO(img_bytes))
                        generated_image.load()  # force decode

                if generated_image:
                    st.markdown("""
                    <div class="result-card">
                        <h2>🎯 Generated Ad Creative</h2>
                    </div>
                    """, unsafe_allow_html=True)

                    st.image(generated_image, caption=f"Ad Creative — {product_name}", width='stretch')

                    # ── Download button ──
                    buf = io.BytesIO()
                    generated_image.save(buf, format="PNG")
                    buf.seek(0)

                    st.download_button(
                        label="📥  Download Ad Creative (PNG)",
                        data=buf,
                        file_name=f"ad_creative_{product_name.lower().replace(' ', '_')}.png",
                        mime="image/png",
                        width='stretch',
                    )

                    if response_text:
                        with st.expander("💬 Model's notes"):
                            st.markdown(response_text)
                else:
                    st.warning("The model did not return an image. This can happen due to safety filters or content policies. Please try again with a different image or prompt.")
                    if response_text:
                        st.info(f"Model response: {response_text}")

            except Exception as e:
                import traceback
                st.error(f"**Generation failed:** {str(e)}")
                st.code(traceback.format_exc(), language="text")
                st.caption("Common issues: invalid API key, quota exceeded, or unsupported image format. Check the sidebar configuration and try again.")


# ──────────────────────────────────────────────
#  Footer
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#6B7280; font-size:.85rem;'>"
    "Powered by <strong>Gemini 3 Pro Image</strong> (Nano Banana Pro) · "
    "Built with Streamlit"
    "</p>",
    unsafe_allow_html=True,
)
