import streamlit as st
import requests
import json

# 1. Page Configuration (Must be at the very top)
st.set_page_config(
    page_title="Multi-API Clothing Store",
    page_icon="👗",
    layout="wide"
)

# Initialize Session State variables for Multi-Page communication
if "cart" not in st.session_state:
    st.session_state.cart = []
if "api_status" not in st.session_state:
    st.session_state.api_status = {"fakestore": "Unknown", "platzi": "Unknown"}

# 2. Define Free API Sources & Links
API_SOURCES = {
    "Fake Store API": {
        "url": "https://fakestoreapi.com",
        "link": "https://fakestoreapi.com",
        "description": "A free REST API for e-commerce testing. Falls back to a local model if servers drop."
    },
    "Platzi Fake Store API": {
        "url": "https://escuelajs.co",
        "link": "https://platzi.com",
        "description": "Real fashion product database. Falls back to a local model if servers drop."
    }
}

# 3. Offline Hardcoded Sandbox Database (Failsafe Backup Layout)
OFFLINE_FAKESTORE_MOCK = [
    {"id": 101, "title": "Premium Denim Trucker Jacket", "price": 89.99, "category": "men's clothing", "description": "Classic fit washed cotton jean jacket with double stitching and iron rivets.", "image": "https://unsplash.com"},
    {"id": 102, "title": "Slim-Fit Vintage Oxford Shirt", "price": 45.00, "category": "men's clothing", "description": "Breathable 100% organic cotton weave ideal for business casual or summer layer sets.", "image": "https://unsplash.com"},
    {"id": 103, "title": "Urban Weatherproof Windbreaker", "price": 110.00, "category": "men's clothing", "description": "Matte finish technical nylon outer shield featuring seamless waterproof thermal zippers.", "image": "https://unsplash.com"}
]

OFFLINE_PLATZI_MOCK = [
    {"id": 201, "title": "Retro Canvas Low-Top Sneakers", "price": 65.50, "description": "Vulcanized heavy-duty rubber sole paired with reinforced stitch breathability profile.", "images": ["https://unsplash.com"]},
    {"id": 202, "title": "Boho A-Line Summer Sundress", "price": 75.00, "description": "Flowing silhouette print dress woven cleanly with custom linen-blend luxury straps.", "images": ["https://unsplash.com"]},
    {"id": 203, "title": "Minimalist Full-Grain Suede Tote", "price": 140.00, "description": "Spacious main structural chamber featuring modular leather zip inserts.", "images": ["https://unsplash.com"]}
]

# 4. Resilient Data Fetchers
@st.cache_data(ttl=60)
def fetch_fake_store_data():
    try:
        res = requests.get("https://fakestoreapi.com", timeout=4)
        if res.status_code == 200 and len(res.json()) > 0:
            st.session_state.api_status["fakestore"] = "Online (Live Data)"
            all_items = res.json()
            clothing = [i for i in all_items if i.get('category', '').lower() in ["men's clothing", "women's clothing"]]
            return clothing if clothing else all_items[:6]
    except Exception:
        pass
    st.session_state.api_status["fakestore"] = "Offline (Using Sandbox Backup)"
    return OFFLINE_FAKESTORE_MOCK

@st.cache_data(ttl=60)
def fetch_platzi_data():
    try:
        res = requests.get("https://escuelajs.co", timeout=4)
        if res.status_code == 200 and len(res.json()) > 0:
            st.session_state.api_status["platzi"] = "Online (Live Data)"
            return res.json()[:6]
    except Exception:
        pass
    st.session_state.api_status["platzi"] = "Offline (Using Sandbox Backup)"
    return OFFLINE_PLATZI_MOCK

def parse_image_url(images_field):
    if not images_field:
        return "https://unsplash.com"
    raw = images_field if isinstance(images_field, list) else str(images_field)
    raw = raw.strip('[]"\' ')
    if "placeimg.com" in raw or not raw.startswith("http"):
        return "https://unsplash.com"
    return raw

# 5. UI Grid Layout Renderer
def render_product_grid(products, source_type):
    cols = st.columns(3)
    for i, item in enumerate(products):
        with cols[i % 3]:
            title = item.get('title', 'Premium Apparel')
            price = item.get('price', 0.0)
            desc = item.get('description', 'High-quality curated collection item.')[:85] + "..."
            image_url = parse_image_url(item.get('image' if source_type == "fakestore" else 'images'))

            with st.container(border=True):
                st.image(image_url, use_container_width=True)
                st.subheader(f"{title[:35]}")
                st.markdown(f"### **\${price}**")
                st.caption(desc)
                
                # Dynamic add to cart handler
                if st.button("Add to Cart", key=f"btn_{source_type}_{item.get('id', i)}"):
                    st.session_state.cart.append({"title": title, "price": price, "image": image_url})
                    st.toast(f"🛒 Added {title[:15]}... to your cart!")

# --- DEFINING INDEPENDENT PAGES ---

def home_page():
    st.title("👗 Multi-API Digital Clothing Boutique")
    st.write("Welcome to the aggregate clothing hub powered concurrently by independent free data platforms.")

    # API Links on Home Page
    st.markdown("### 🔗 Direct API Documentation Links")
    api_cols = st.columns(2)
    for idx, (name, info) in enumerate(API_SOURCES.items()):
        with api_cols[idx]:
            with st.container(border=True):
                st.markdown(f"#### **[{name}]({info['link']})**")
                st.write(info['description'])
                st.caption(f"Endpoint: `{info['url']}`")

    st.markdown("---")

    # Catalog Sections
    st.markdown("### 🗂️ Explore Collections")
    app_mode = st.segmented_control(
        "Choose a Store Section:", 
        options=["All Clothing", "Fake Store API Inventory", "Platzi Fashion API Inventory"],
        default="All Clothing"
    )

    fake_store_products = fetch_fake_store_data()
    platzi_products = fetch_platzi_data()

    if app_mode == "All Clothing":
        st.markdown("### 🏷️ From: Fake Store API Section")
        render_product_grid(fake_store_products, "fakestore")
        st.markdown("---")
        st.markdown("### 🏷️ From: Platzi Fashion API Section")
        render_product_grid(platzi_products, "platzi")
    elif app_mode == "Fake Store API Inventory":
        render_product_grid(fake_store_products, "fakestore")
    elif app_mode == "Platzi Fashion API Inventory":
        render_product_grid(platzi_products, "platzi")

def cart_page():
    st.title("🛍️ Your Shopping Cart")
    st.write("Review your collected items pulled directly via remote web nodes.")
    
    if not st.session_state.cart:
        st.info("Your cart is currently empty. Go back to the storefront to add fashion items!")
        return
        
    total_cost = sum(item['price'] for item in st.session_state.cart)
    
    # Display total summary row
    st.metric(label="Total Order Value", value=f"\${total_cost:,.2f}")
    if st.button("Clear Cart"):
        st.session_state.cart = []
        st.rerun()
        
    st.markdown("---")
    
    # Render horizontal items list inside the cart page
    for idx, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([1, 4, 1])
        with c1:
            st.image(item['image'], width=80)
        with c2:
            st.markdown(f"#### {item['title']}")
        with c3:
            st.markdown(f"### **\${item['price']}**")
        st.markdown("---")

def status_page():
    st.title("📊 Multi-API System Status & Diagnostics")
    st.write("Real-time network connection monitor tracking data status hooks.")
    
    # Execute dummy fetches to update variables before drawing status boards
    fetch_fake_store_data()
    fetch_platzi_data()
    
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("Fake Store API Network")
            status = st.session_state.api_status["fakestore"]
            if "Online" in status:
                st.success(status)
            else:
                st.error(status)
            st.caption(f"Target Feed URL: `{API_SOURCES['Fake Store API']['url']}`")
            
    with col2:
        with st.container(border=True):
            st.subheader("Platzi Fashion API Network")
            status = st.session_state.api_status["platzi"]
            if "Online" in status:
                st.success(status)
            else:
                st.error(status)
            st.caption(f"Target Feed URL: `{API_SOURCES['Platzi Fake Store API']['url']}`")

# --- NATIVE TOP NAVIGATION BAR CONTROL ---
st.markdown("## 🧭 Store Navigation")
current_tab = st.segmented_control(
    "Switch App Views:",
    options=["🏠 Shop Catalog", f"🛍️ Checkout ({len(st.session_state.cart)} items)", "📊 API System Status"],
    default="🏠 Shop Catalog"
)
st.markdown("---")

# Render the page based on the selected tab
if "Shop Catalog" in current_tab:
    home_page()
elif "Checkout" in current_tab:
    cart_page()
elif "API System Status" in current_tab:
    status_page()
