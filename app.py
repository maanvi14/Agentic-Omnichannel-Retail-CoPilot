from typing import List, Dict, Any
from datetime import datetime
from io import BytesIO
import os

import streamlit as st
import pandas as pd
import qrcode

from langchain_core.messages import HumanMessage, AIMessage

try:
    from retail_agent_langgraph import (
        graph,
        CUSTOMERS,
        PRODUCT_CATALOG,
        INVENTORY,
        pos_terminal_agent,
    )
except ImportError as e:
        st.error(
            "Failed to import `retail_agent_langgraph`. "
            "Ensure it is in the working directory and all dependencies "
            "(langgraph, langchain-core, langgraph, etc.) are installed."
        )
        raise e

PRODUCT_URLS: Dict[str, str] = {
    "Nike Air Max 90 - Red": "https://www.nike.com/launch/t/air-max-90-1-white-university-red",
    "Nike Air Max 90 - Black": "https://www.nike.com/t/air-max-90-ltr-big-kids-shoes-1wzwJM/CD6864-028",
    "Nike Air Max 90 - White": "https://www.farfetch.com/in/shopping/women/nike-air-max-90-white-reptile-sneakers-item-20053304.aspx",
    "Nike React Infinity Run - Pink": "https://www.techwheels.in/?d=60741000031910",
}

st.set_page_config(
    page_title="Agentic Omnichannel Retail CoPilot",
    layout="wide",
)

st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"], .main {
        background: radial-gradient(circle at top, #111827 0%, #020617 45%, #000000 100%) !important;
        color: #e5e7eb !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 1250px !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid #111827 !important;
        box-shadow: 4px 0 12px rgba(0,0,0,0.6);
        color: #e5e7eb !important;
    }

    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] label {
        color: #e5e7eb !important;
    }

    section[data-testid="stSidebar"] .stTextInput > div > div > input,
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: #020617 !important;
        color: #e5e7eb !important;
        border-radius: 999px !important;
        border: 1px solid #374151 !important;
    }

    div[data-baseweb="tab-list"] {
        border-bottom: 1px solid #1f2937 !important;
    }

    button[data-baseweb="tab"] {
        font-size: 0.95rem !important;
        padding-bottom: 2px !important;
        font-weight: 600 !important;
        color: #e5e7eb !important;
        background: transparent !important;
        border-bottom: 2px solid transparent !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 2px solid #facc15 !important;
        color: #ffffff !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3px solid #facc15 !important;
        color: #ffffff !important;
    }

    .section-card {
        background: #020617 !important;
        border-radius: 16px !important;
        padding: 22px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.7) !important;
        border: 1px solid #111827 !important;
    }

    .section-title {
        font-weight: 600 !important;
        color: #f9fafb !important;
        font-size: 1.1rem !important;
        margin-bottom: 4px !important;
    }

    .section-subtitle {
        font-size: 0.88rem !important;
        color: #9ca3af !important;
        margin-bottom: 14px !important;
    }

    .product-card {
        background: #020617 !important;
        border-radius: 14px !important;
        padding: 14px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.8) !important;
        border: 1px solid #1f2937 !important;
        transition: transform 0.12s ease-in-out, box-shadow 0.12s ease-in-out;
    }

    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.9) !important;
    }

    .product-card h4 {
        font-weight: 600 !important;
        color: #f9fafb !important;
        font-size: 0.96rem !important;
    }

    .product-card .price {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #facc15 !important;
    }

    .product-card .sku {
        font-size: 0.78rem !important;
        color: #9ca3af !important;
    }

    .availability-badge {
        display: inline-block;
        border-radius: 999px;
        padding: 2px 8px;
        font-size: 11px;
        margin-left: 4px;
    }

    .stButton > button {
        border-radius: 999px !important;
        background: linear-gradient(135deg, #facc15, #f59e0b) !important;
        color: #111827 !important;
        padding: 0.5rem 1.3rem !important;
        border: none !important;
        font-size: 0.86rem !important;
        font-weight: 600 !important;
        transition: 0.2s ease-in-out;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #fbbf24, #ea580c) !important;
        box-shadow: 0px 4px 14px rgba(250, 204, 21, 0.45);
        transform: translateY(-2px);
    }

    .stTextInput > div > div > input {
        border-radius: 12px !important;
        padding: 10px 14px !important;
        background: #020617 !important;
        border: 1px solid #374151 !important;
        color: #e5e7eb !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #6b7280 !important;
    }

    .stSelectbox > div > div {
        border-radius: 12px !important;
        background: #020617 !important;
        border: 1px solid #374151 !important;
        color: #e5e7eb !important;
    }

    .stSelectbox label {
        color: #e5e7eb !important;
    }

    div[data-testid="stChatMessage"] {
        background: #020617 !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 12px !important;
        border: 1px solid #1f2937 !important;
        box-shadow: 0 4px 14px rgba(0,0,0,0.8);
    }

    div[data-testid="stChatMessage"] p {
        font-size: 0.92rem !important;
        color: #e5e7eb !important;
    }

    .stDataFrame, .stTable {
        background: #020617 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid #1f2937 !important;
        color: #e5e7eb !important;
    }

    .stDataFrame table, .stTable table {
        color: #e5e7eb !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "graph_state" not in st.session_state:
    st.session_state.graph_state = None

if "reservations" not in st.session_state:
    st.session_state.reservations: List[Dict[str, Any]] = []

if "orders" not in st.session_state:
    st.session_state.orders: List[Dict[str, Any]] = []

if "last_failed_card" not in st.session_state:
    st.session_state.last_failed_card: Dict[str, Any] | None = None


def ensure_graph_state(channel: str, customer_id: str) -> None:
    if (
        st.session_state.graph_state is None
        or st.session_state.graph_state.get("customer_id") != customer_id
    ):
        st.session_state.graph_state = {
            "messages": [],
            "channel": channel,
            "customer_id": customer_id,
            "customer_profile": CUSTOMERS[customer_id],
        }
    else:
        st.session_state.graph_state["channel"] = channel
        st.session_state.graph_state["customer_id"] = customer_id
        st.session_state.graph_state["customer_profile"] = CUSTOMERS[customer_id]


def invoke_agent(user_text: str, channel: str, customer_id: str) -> str:
    ensure_graph_state(channel, customer_id)
    state = st.session_state.graph_state
    state["messages"].append(HumanMessage(content=user_text))
    new_state = graph.invoke(state)
    st.session_state.graph_state = new_state

    for msg in reversed(new_state["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content
    return "(No AI response)"


def render_chat_history() -> None:
    if st.session_state.graph_state is None:
        return
    for msg in st.session_state.graph_state["messages"]:
        if isinstance(msg, HumanMessage):
            st.chat_message("user").markdown(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").markdown(msg.content)


def filter_products(query: str, brand_filter: str) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    q = query.lower().strip()
    for p in PRODUCT_CATALOG:
        if brand_filter != "All" and p["brand"].lower() != brand_filter.lower():
            continue
        if q:
            haystack = " ".join(
                [
                    p["name"].lower(),
                    p.get("color", "").lower(),
                    " ".join(p.get("tags", [])),
                    p.get("collection", "").lower(),
                ]
            )
            if q not in haystack:
                continue
        results.append(p)
    return results


def format_store_availability(sku: str) -> str:
    rows = []
    stock_info = INVENTORY.get(sku, {})
    for store, qty in stock_info.items():
        if store == "ONLINE":
            continue
        if qty == 0:
            bg = "#450a0a"
            fg = "#fecaca"
            status = "Out of stock"
        elif qty <= 2:
            bg = "#3b2f0b"
            fg = "#facc15"
            status = f"{qty} left"
        else:
            bg = "#052e16"
            fg = "#bbf7d0"
            status = f"{qty} in stock"
        rows.append(
            f"<div style='margin-bottom:2px;'>"
            f"<span style='font-weight:600;color:#e5e7eb;'>{store}</span>"
            f"<span class='availability-badge' style='background:{bg}; color:{fg};'>{status}</span>"
            f"</div>"
        )
    return "".join(rows)


def generate_qr_image(data: str) -> BytesIO:
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def create_reservation(sku: str, store: str) -> Dict[str, Any]:
    base_id = sku.replace("_", "")
    number = len(st.session_state.reservations) + 1
    reservation_id = f"RS-{base_id}-{number}"
    record = {
        "id": reservation_id,
        "sku": sku,
        "store": store,
        "status": "active",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    st.session_state.reservations.append(record)
    return record


def add_order(sku: str, store: str, amount: float, status: str = "completed") -> Dict[str, Any]:
    order_id = f"ORD-{sku.replace('_', '')}-{len(st.session_state.orders)+1}"
    record = {
        "id": order_id,
        "sku": sku,
        "store": store,
        "amount": amount,
        "status": status,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    st.session_state.orders.append(record)
    return record


with st.sidebar:
    st.header("Configuration")

    groq_default = st.session_state.get("GROQ_API_KEY", "")
    groq_key = st.text_input(
        "Groq API key",
        value=groq_default,
        type="password",
        help="Used by the LangGraph / Groq-powered retail agent.",
    )
    if groq_key:
        st.session_state["GROQ_API_KEY"] = groq_key
        os.environ["GROQ_API_KEY"] = groq_key

    channel = st.selectbox(
        "Channel",
        ["mobile_app", "web", "whatsapp", "kiosk", "pos"],
        index=0,
    )

    customer_id = st.selectbox("Customer profile", list(CUSTOMERS.keys()), index=0)
    profile = CUSTOMERS[customer_id]

    st.markdown("---")
    st.write(f"**Name**: {profile['name']}")
    st.write(f"**City**: {profile['city']}")
    st.write(f"**Loyalty Tier**: {profile['loyalty_tier']}")
    st.write(f"**Style Preferences**: {', '.join(profile['style_preference'])}")
    st.write(f"**Budget Range**: {profile['budget_range']}")

    if st.button("Reset conversation and state"):
        st.session_state.graph_state = None
        st.session_state.reservations = []
        st.session_state.orders = []
        st.session_state.last_failed_card = None
        st.experimental_rerun()

    st.markdown("---")
    with st.expander("Reservations and orders", expanded=False):
        if st.session_state.reservations:
            st.markdown("**Active reservations**")
            st.table(
                [
                    {
                        "ID": r["id"],
                        "SKU": r["sku"],
                        "Store": r["store"],
                        "Status": r["status"],
                    }
                    for r in st.session_state.reservations
                ]
            )
        else:
            st.caption("No reservations yet.")

        if st.session_state.orders:
            st.markdown("**Order history**")
            st.table(
                [
                    {
                        "ID": o["id"],
                        "SKU": o["sku"],
                        "Store": o["store"],
                        "Amount": o["amount"],
                        "Status": o["status"],
                    }
                    for o in st.session_state.orders
                ]
            )
        else:
            st.caption("No completed orders yet.")

st.title("Agentic Omnichannel Retail CoPilot")
st.caption(
    "This demo replicates the exact agent flow implemented in Python using LangGraph, Groq tool-calling, inventory APIs, SKU normalization, and multi-channel retail behaviors."
)

tab1, tab2, tab3 = st.tabs(
    ["Customer App", "In-Store Kiosk / POS", "Manager Dashboard"]
)

with tab1:
    left_col, right_col = st.columns([1.05, 1.95])

    with left_col:
        st.markdown(
            "<div class='section-card'>"
            "<div class='section-title'>AI-powered retail assistance</div>",
            unsafe_allow_html=True,
        )

        render_chat_history()
        user_query = st.chat_input(
            "Type a message to the sales agent…", key="customer_chat_input"
        )
        if user_query:
            st.chat_message("user").markdown(user_query)
            reply = invoke_agent(user_query, channel, customer_id)
            st.chat_message("assistant").markdown(reply)
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown(
            "<div class='section-card'>"
            "<div class='section-title'>Product catalogue</div>"
            "<div class='section-subtitle'>Search the catalogue, then reserve or buy.</div>",
            unsafe_allow_html=True,
        )

        unique_brands = sorted({p["brand"] for p in PRODUCT_CATALOG})
        col_filter1, col_filter2 = st.columns([1.1, 1.4])
        with col_filter1:
            brand_filter = st.selectbox("Brand filter", ["All"] + unique_brands, index=0)
        with col_filter2:
            search_query = st.text_input(
                "Search by name, colour, tags or collection",
                "",
                key="product_search_input",
            )

        filtered = filter_products(search_query, brand_filter)
        if not filtered:
            st.info("No products match this query.")
        else:
            cols = st.columns(2)
            for idx, p in enumerate(filtered):
                with cols[idx % 2]:
                    st.markdown("<div class='product-card'>", unsafe_allow_html=True)
                    st.image(p["image_url"], use_container_width=True)
                    st.markdown(f"<h4>{p['name']}</h4>", unsafe_allow_html=True)
                    st.markdown(
                        f"<div class='price'>₹{p['price']:,}</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"<div class='sku'>SKU: {p['sku']}</div>",
                        unsafe_allow_html=True,
                    )

                    availability_html = format_store_availability(p["sku"])
                    if availability_html:
                        st.markdown(availability_html, unsafe_allow_html=True)

                    sku = p["sku"]
                    product_url = p.get("product_url") or PRODUCT_URLS.get(p["name"])

                    b1, b2, b3 = st.columns(3)

                    if b1.button("Check stores", key=f"check_{sku}"):
                        q = f"Check availability of {sku} in all stores."
                        st.chat_message("user").markdown(q)
                        resp = invoke_agent(q, channel, customer_id)
                        st.chat_message("assistant").markdown(resp)

                    if b2.button("Reserve", key=f"reserve_{sku}"):
                        store = "Pacific Mall"
                        record = create_reservation(sku, store)
                        st.success(
                            f"Reservation created for {sku} at {store}. "
                            f"ID: {record['id']} (valid for 2 hours)."
                        )

                        qr_buf = generate_qr_image(record["id"])
                        st.image(
                            qr_buf,
                            caption=record["id"],
                            use_container_width=False,
                        )

                        msg = (
                            f"Please create a reservation for {sku} at {store} with "
                            f"reservation ID {record['id']}."
                        )
                        resp = invoke_agent(msg, "whatsapp", customer_id)
                        st.chat_message("assistant").markdown(resp)

                    if b3.button("Buy now", key=f"buy_{sku}"):
                        msg = f"I want to buy {sku} using my credit card."
                        st.chat_message("user").markdown(msg)
                        resp = invoke_agent(msg, channel, customer_id)
                        st.chat_message("assistant").markdown(resp)
                        st.info(
                            "Move to the In-Store Kiosk / POS tab to simulate billing "
                            "and payment."
                        )

                    if product_url:
                        st.markdown(
                            f"<div style='margin-top:6px;'>"
                            f"<a href='{product_url}' target='_blank' "
                            f"style='font-size:0.8rem;color:#60a5fa;text-decoration:none;'>"
                            f"View full product page ↗"
                            f"</a></div>",
                            unsafe_allow_html=True,
                        )

                    st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    col_k1, col_k2 = st.columns([1.2, 1.0])

    with col_k1:
        st.markdown(
            "<div class='section-card'>"
            "<div class='section-title'>Kiosk conversation</div>"
            "<div class='section-subtitle'>Continue the same session when the customer reaches the store.</div>",
            unsafe_allow_html=True,
        )
        render_chat_history()
        kiosk_input = st.text_input(
            "Kiosk message (optional)",
            "",
            key="kiosk_text_input",
            placeholder="I am at Pacific Mall now, show my reserved shoes.",
        )
        if st.button("Send kiosk message", key="kiosk_send") and kiosk_input.strip():
            st.chat_message("user").markdown(kiosk_input)
            reply = invoke_agent(kiosk_input, "kiosk", customer_id)
            st.chat_message("assistant").markdown(reply)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_k2:
        st.markdown(
            "<div class='section-card'>"
            "<div class='section-title'>QR reservation scanning</div>"
            "<div class='section-subtitle'>Simulate scanning the reservation QR at the kiosk.</div>",
            unsafe_allow_html=True,
        )

        reservation_ids = [r["id"] for r in st.session_state.reservations]
        selected_res = st.selectbox(
            "Select an existing reservation or type it below",
            ["(type manually)"] + reservation_ids,
            index=0,
        )
        manual_id = st.text_input(
            "Reservation ID",
            "",
            key="manual_res_id",
            placeholder="e.g., RS-AM90-1",
        )

        def _get_res_id() -> str | None:
            if selected_res != "(type manually)":
                return selected_res
            if manual_id.strip():
                return manual_id.strip()
            return None

        if st.button("Scan QR at kiosk", key="btn_scan_qr"):
            res_id = _get_res_id()
            if not res_id:
                st.warning("Please select or type a reservation ID first.")
            else:
                msg = f"I have scanned my QR with reservation ID {res_id} at the kiosk."
                st.chat_message("user").markdown(msg)
                reply = invoke_agent(msg, "kiosk", customer_id)
                st.chat_message("assistant").markdown(reply)
                st.success("The kiosk has accepted the reservation. Proceed to billing.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-card'>"
        "<div class='section-title'>POS billing and payment</div>"
        "<div class='section-subtitle'>Trigger card payment and, if needed, fall back to UPI with a dynamic QR code.</div>",
        unsafe_allow_html=True,
    )

    sku_pos = st.selectbox(
        "Product SKU",
        [p["sku"] for p in PRODUCT_CATALOG],
        key="pos_sku",
    )
    store_pos = st.selectbox(
        "Store location",
        ["Motinagar", "Pacific Mall", "DLF Promenade", "Kamla Nagar"],
        key="pos_store",
    )
    payment_method = st.selectbox(
        "Primary payment method",
        ["card", "upi"],
        key="pos_payment",
    )

    product_pos = next(p for p in PRODUCT_CATALOG if p["sku"] == sku_pos)
    amount = product_pos["price"]

    if st.button("Process POS payment", key="pos_pay"):
        result = pos_terminal_agent.invoke(
            {"sku": sku_pos, "store": store_pos, "payment_method": payment_method}
        )

        if result.get("status") == "success":
            st.success(
                f"POS billing successful. Receipt ID: {result['pos_receipt_id']}."
            )
            add_order(sku_pos, store_pos, amount)

            msg = (
                f"Payment completed successfully at POS for {sku_pos} at {store_pos}. "
                f"Please confirm the order and award loyalty points."
            )
            reply = invoke_agent(msg, "whatsapp", customer_id)
            st.chat_message("assistant").markdown(reply)

        else:
            reason = result.get("reason", "Card declined")
            st.error(f"Payment failed: {reason}")

            if payment_method == "card":
                st.warning("Switching to UPI QR fallback for this transaction.")
                upi_link = (
                    f"upi://pay?pa=merchant@upi&am={amount}&tn={sku_pos}-{store_pos}"
                )
                qr_buf = generate_qr_image(upi_link)
                st.image(
                    qr_buf,
                    caption="Scan to pay via UPI (simulated)",
                    use_container_width=False,
                )

                st.session_state.last_failed_card = {
                    "sku": sku_pos,
                    "store": store_pos,
                    "amount": amount,
                }

    if st.session_state.last_failed_card is not None:
        failed = st.session_state.last_failed_card
        if st.button("Confirm UPI payment", key="confirm_upi"):
            st.success("UPI payment confirmed (simulated). Order completed.")
            order = add_order(
                failed["sku"], failed["store"], failed["amount"], status="completed"
            )
            st.session_state.last_failed_card = None

            msg = (
                f"The card payment had failed, but UPI payment is now successful for "
                f"order {order['id']} ({order['sku']} at {order['store']}). "
                f"Please confirm the purchase and add loyalty points."
            )
            reply = invoke_agent(msg, "whatsapp", customer_id)
            st.chat_message("assistant").markdown(reply)

    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown(
        "<div class='section-card'>"
        "<div class='section-title'>Inventory signals</div>"
        "<div class='section-subtitle'>Low stock and demand indicators to support store decisions.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("**Low stock alerts**")
    alerts = []
    for sku, stores in INVENTORY.items():
        for store, qty in stores.items():
            if store != "ONLINE" and qty <= 1:
                product = next(p for p in PRODUCT_CATALOG if p["sku"] == sku)
                alerts.append(
                    {"SKU": sku, "Product": product["name"], "Store": store, "Qty": qty}
                )
    if alerts:
        st.dataframe(pd.DataFrame(alerts))
    else:
        st.success("No low stock alerts at the moment.")

    st.markdown("---")
    st.markdown("**Simple demand indicator (illustrative)**")
    demand_rows = []
    for sku, stores in INVENTORY.items():
        product = next(p for p in PRODUCT_CATALOG if p["sku"] == sku)
        for store, qty in stores.items():
            if store == "ONLINE":
                continue
            demand = max(5, 20 - qty)
            if product["brand"].lower() == "nike":
                demand += 5
            demand_rows.append(
                {
                    "Store": store,
                    "SKU": sku,
                    "Product": product["name"],
                    "Current Stock": qty,
                    "Demand Score (relative)": demand,
                }
            )
    st.dataframe(pd.DataFrame(demand_rows))

    st.markdown("</div>", unsafe_allow_html=True)
