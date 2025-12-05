import os
from typing import Annotated, TypedDict, Literal
from datetime import datetime

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_groq import ChatGroq
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool





# 2. LangGraph Shared State

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    channel: str
    customer_profile: dict


# ------------------------------------------------------------
# 3. PRODUCT CATALOG
# ------------------------------------------------------------
PRODUCT_CATALOG = [
    {
        "sku": "DRESS001",
        "name": "Black Party Dress",
        "category": "dress",
        "gender": "female",
        "price": 2499,
        "occasion": ["party", "evening"],
        "color": "black",
        "brand": "ABFRL",
        "image_url": "https://littleboxindia.com/cdn/shop/files/Square_Neck_Ruched_Ruffle_Black_Mini_Dress_720x.jpg?v=1741087948",
    },
    {
        "sku": "SHOE001",
        "name": "Silver Heels",
        "category": "shoes",
        "gender": "female",
        "price": 1999,
        "occasion": ["party", "wedding"],
        "color": "silver",
        "brand": "ABFRL",
        "image_url": "https://www.mytheresa.com/media/2310/2612/100/ee/P00642615.jpg",
    },
    {
        "sku": "TSHIRT001",
        "name": "Casual White T-Shirt",
        "category": "topwear",
        "gender": "unisex",
        "price": 799,
        "occasion": ["casual"],
        "color": "white",
        "brand": "ABFRL",
        "image_url": "https://image.hm.com/assets/hm/57/ac/57ac952411da3dd2c221d31f22991434fb577b23.jpg?imwidth=1260",
    },

    # --- Nike Collection ---
    {
        "sku": "NIKE_AM90_RED",
        "name": "Nike Air Max 90 - Red",
        "category": "shoes",
        "gender": "unisex",
        "price": 5000,
        "brand": "Nike",
        "color": "red",
        "occasion": ["sports", "running", "lifestyle"],
        "image_url": "https://cdn-images.farfetch-contents.com/19/85/63/68/19856368_45060991_600.jpg",
    },
    {
        "sku": "NIKE_AM90_BLACK",
        "name": "Nike Air Max 90 - Black",
        "category": "shoes",
        "gender": "unisex",
        "price": 5000,
        "brand": "Nike",
        "color": "black",
        "occasion": ["sports", "running"],
        "image_url": "https://static.nike.com/a/images/t_web_pdp_535_v2/f_auto/17e9f8b3-557c-4e5f-9d72-729d378f9557/WMNS+AIR+MAX+90.png",
    },
    {
        "sku": "NIKE_AM90_WHITE",
        "name": "Nike Air Max 90 - White",
        "category": "shoes",
        "gender": "unisex",
        "price": 5000,
        "brand": "Nike",
        "color": "white",
        "occasion": ["sports", "casual"],
        "image_url": "https://static.nike.com/a/images/t_web_pw_592_v2/f_auto/5c2d3b6e-cbfa-4944-9573-6e62c521e517/WMNS+NIKE+AIR+MAX+EXCEE.png",
    },
    {
        "sku": "NIKE_REACT_PINK",
        "name": "Nike React Infinity Run - Pink",
        "category": "shoes",
        "gender": "female",
        "price": 5200,
        "brand": "Nike",
        "color": "pink",
        "occasion": ["running", "training"],
        "image_url": "https://en-qa.sssports.com/dw/image/v2/BDVB_PRD/on/demandware.static/-/Sites-akeneo-master-catalog/default/dwf28aa7f2/sss/SSS2/N/K/D/D/3/SSS2_NKDD3024_600_195868914672_1.jpg",
    },

    # Apparel
    {
        "sku": "KURTA001",
        "name": "Blue Festive Kurta",
        "category": "ethnic",
        "gender": "male",
        "price": 2999,
        "occasion": ["festive", "wedding"],
        "color": "blue",
        "brand": "ABFRL",
        "image_url": "https://static3.azafashions.com/tr:w-450/uploads/product_gallery/1702290276317_1.jpg",
    },
    {
        "sku": "JEANS001",
        "name": "Slim Fit Jeans",
        "category": "bottomwear",
        "gender": "male",
        "price": 1999,
        "occasion": ["casual"],
        "color": "dark_blue",
        "brand": "ABFRL",
        "image_url": "https://image.hm.com/assets/hm/94/c7/94c7784148c73a94544ae78a65fb5e6b1580e462.jpg?imwidth=2160",
    },
]


# ------------------------------------------------------------
# 4. INVENTORY DATABASE
# ------------------------------------------------------------
INVENTORY = {
    "DRESS001": {"ONLINE": 20, "Motinagar": 3, "Pacific Mall": 2, "DLF Promenade": 0, "Kamla Nagar": 1},
    "SHOE001": {"ONLINE": 15, "Motinagar": 1, "Pacific Mall": 0, "DLF Promenade": 2, "Kamla Nagar": 0},
    "TSHIRT001": {"ONLINE": 50, "Motinagar": 10, "Pacific Mall": 5, "DLF Promenade": 4, "Kamla Nagar": 0},
    "NIKE_AM90_RED": {"ONLINE": 10, "Motinagar": 2, "Pacific Mall": 3, "DLF Promenade": 0, "Kamla Nagar": 1},
    "NIKE_AM90_BLACK": {"ONLINE": 12, "Motinagar": 0, "Pacific Mall": 4, "DLF Promenade": 2, "Kamla Nagar": 0},
    "NIKE_AM90_WHITE": {"ONLINE": 8, "Motinagar": 1, "Pacific Mall": 2, "DLF Promenade": 0, "Kamla Nagar": 1},
    "NIKE_REACT_PINK": {"ONLINE": 6, "Motinagar": 0, "Pacific Mall": 1, "DLF Promenade": 3, "Kamla Nagar": 0},
    "KURTA001": {"ONLINE": 10, "Motinagar": 1, "Pacific Mall": 2, "DLF Promenade": 1, "Kamla Nagar": 0},
    "JEANS001": {"ONLINE": 20, "Motinagar": 3, "Pacific Mall": 3, "DLF Promenade": 2, "Kamla Nagar": 1},
}


# ------------------------------------------------------------
# 5. PROMOTIONS
# ------------------------------------------------------------
PROMOTIONS = {
    "LOYALTY_GOLD": {"discount_percent": 10, "description": "10% off for Gold members."},
    "LOYALTY_SILVER": {"discount_percent": 5, "description": "5% off for Silver members."},
    "WEEKEND_SALE": {
        "discount_percent": 7,
        "description": "Weekend online sale.",
        "days_active": ["SATURDAY", "SUNDAY"],
    },
}


# ------------------------------------------------------------
# 6. CUSTOMER PROFILES
# ------------------------------------------------------------
CUSTOMERS = {
    "maanvi": {
        "name": "Maanvi Verma",
        "age": 20,
        "gender": "female",
        "city": "New Delhi",
        "loyalty_tier": "GOLD",
        "preferred_channel": "mobile_app",
        "device_preference": ["mobile", "whatsapp"],
        "past_purchases": ["TSHIRT001", "SHOE001"],
        "shoe_size": 6,
        "style_preference": ["casual", "sports"],
        "budget_range": "2000-6000",
    },
    "manishika": {
        "name": "Manishika Gupta",
        "age": 21,
        "gender": "female",
        "city": "New Delhi",
        "loyalty_tier": "SILVER",
        "preferred_channel": "kiosk",
        "device_preference": ["mobile"],
        "past_purchases": ["NIKE_AM90_RED"],
        "shoe_size": 7,
        "style_preference": ["sports", "running"],
        "budget_range": "3000-7000",
    },
    "rahul": {
        "name": "Rahul Singh",
        "age": 24,
        "gender": "male",
        "city": "Bengaluru",
        "loyalty_tier": "NONE",
        "preferred_channel": "web",
        "device_preference": ["desktop"],
        "past_purchases": [],
        "shoe_size": 9,
        "style_preference": ["lifestyle"],
        "budget_range": "1500-3500",
    },
    "aisha": {
        "name": "Aisha Khan",
        "age": 26,
        "gender": "female",
        "city": "Mumbai",
        "loyalty_tier": "GOLD",
        "preferred_channel": "whatsapp",
        "device_preference": ["mobile"],
        "past_purchases": ["DRESS001"],
        "shoe_size": 5,
        "style_preference": ["party", "evening"],
        "budget_range": "3000-8000",
    },
    "arjun": {
        "name": "Arjun Mehta",
        "age": 28,
        "gender": "male",
        "city": "Gurugram",
        "loyalty_tier": "SILVER",
        "preferred_channel": "mobile_app",
        "device_preference": ["mobile"],
        "past_purchases": ["JEANS001"],
        "shoe_size": 10,
        "style_preference": ["casual"],
        "budget_range": "2000-5000",
    },
    "neha": {
        "name": "Neha Sharma",
        "age": 23,
        "gender": "female",
        "city": "Pune",
        "loyalty_tier": "NONE",
        "preferred_channel": "web",
        "device_preference": ["laptop"],
        "past_purchases": [],
        "shoe_size": 6,
        "style_preference": ["ethnic", "festive"],
        "budget_range": "2500-6000",
    },
    "vivek": {
        "name": "Vivek Rao",
        "age": 30,
        "gender": "male",
        "city": "Hyderabad",
        "loyalty_tier": "GOLD",
        "preferred_channel": "mobile_app",
        "device_preference": ["mobile"],
        "past_purchases": ["KURTA001"],
        "shoe_size": 9,
        "style_preference": ["festive"],
        "budget_range": "3000-7000",
    },
    "priya": {
        "name": "Priya Nair",
        "age": 27,
        "gender": "female",
        "city": "Chennai",
        "loyalty_tier": "SILVER",
        "preferred_channel": "whatsapp",
        "device_preference": ["mobile"],
        "past_purchases": ["TSHIRT001"],
        "shoe_size": 6,
        "style_preference": ["casual", "sports"],
        "budget_range": "1500-4000",
    },
    "siddharth": {
        "name": "Siddharth Jain",
        "age": 22,
        "gender": "male",
        "city": "Jaipur",
        "loyalty_tier": "NONE",
        "preferred_channel": "web",
        "device_preference": ["desktop"],
        "past_purchases": [],
        "shoe_size": 8,
        "style_preference": ["casual"],
        "budget_range": "1500-3000",
    },
    "tanya": {
        "name": "Tanya Roy",
        "age": 25,
        "gender": "female",
        "city": "Kolkata",
        "loyalty_tier": "GOLD",
        "preferred_channel": "mobile_app",
        "device_preference": ["mobile"],
        "past_purchases": ["NIKE_REACT_PINK"],
        "shoe_size": 6,
        "style_preference": ["running", "training"],
        "budget_range": "3000-7000",
    },
}


# ------------------------------------------------------------
# 7. TOOLS
# ------------------------------------------------------------

# ------------------------------------------------------------
# 7. TOOLS  (ALL FIXED WITH PROPER DOCSTRINGS)
# ------------------------------------------------------------

@tool
def product_catalog_api(query: str = None, category: str = None, max_price: float = None, brand: str = None):
    """
    Product Catalog API.
    Filters products by query, category, brand and price.
    """
    results = []
    q = (query or "").lower()
    for p in PRODUCT_CATALOG:
        if category and p["category"] != category:
            continue
        if brand and p["brand"].lower() != brand.lower():
            continue
        if max_price and p["price"] > max_price:
            continue
        if q and q not in p["name"].lower() and q not in p["color"]:
            continue
        results.append(p)
    return results


@tool
def recommendation_agent(query: str, customer_id: str = None):
    """
    Recommender agent.
    Scores catalog items using simple keyword-based matching.
    """
    q = query.lower()
    matches = []
    for p in PRODUCT_CATALOG:
        score = 0
        if p["brand"].lower() in q: score += 2
        if p["category"] in q: score += 1
        if p["color"] in q: score += 1
        for occ in p["occasion"]:
            if occ in q:
                score += 1
        if score > 0:
            matches.append({
                "sku": p["sku"],
                "name": p["name"],
                "price": p["price"],
                "brand": p["brand"],
                "score": score
            })
    matches.sort(key=lambda x: (-x["score"], x["price"]))
    return matches[:4]


@tool
def inventory_agent(sku: str, preferred_store: str = None):
    """
    Inventory Service.
    Returns real-time stock levels for online & all stores.
    """
    stock = INVENTORY.get(sku, {})
    if not stock:
        return {"status": "unknown_sku"}

    output = {"sku": sku, "status": "available", "locations": []}
    for store, qty in stock.items():
        output["locations"].append({
            "location": store,
            "quantity": qty,
            "is_preferred": (store == preferred_store)
        })
    return output


@tool
def loyalty_promotions_agent(customer_id: str, channel: str = "mobile_app"):
    """
    Loyalty & Promotions Engine.
    Applies loyalty tier discounts + weekend promo (if applicable).
    """
    profile = CUSTOMERS.get(customer_id)
    if not profile:
        return {"has_offer": False}

    offers = []
    tier = profile["loyalty_tier"]
    weekday = datetime.now().strftime("%A").upper()

    if tier in ("GOLD", "SILVER"):
        offers.append(PROMOTIONS[f"LOYALTY_{tier}"])

    if weekday in PROMOTIONS["WEEKEND_SALE"]["days_active"] and channel == "mobile_app":
        offers.append(PROMOTIONS["WEEKEND_SALE"])

    return {
        "has_offer": len(offers) > 0,
        "tier": tier,
        "offers": offers,
        "total_discount_percent": sum(o["discount_percent"] for o in offers)
    }


@tool
def payment_gateway_stub(amount: float, method: str = "card", step: str = "authorize", channel: str = "online"):
    """
    Payment Gateway Simulation.
    Declines card payments above ₹4000 to simulate limit exceeded.
    """
    if method == "card" and amount > 4000:
        return {"status": "declined", "reason": "Card limit exceeded. Try UPI or split payment."}
    return {
        "status": "approved",
        "transaction_id": "PAY12345",
        "amount": amount,
        "method": method
    }


@tool
def pos_terminal_agent(sku: str, store: str, payment_method: str = "card"):
    """
    POS Billing Agent.
    Simulates in-store POS barcode scan + billing.
    """
    if store not in INVENTORY.get(sku, {}):
        return {"status": "error", "message": "Unknown store"}

    if INVENTORY[sku][store] <= 0:
        return {"status": "failed", "reason": "Item out of stock at POS."}

    return {
        "status": "success",
        "sku": sku,
        "store": store,
        "payment_method": payment_method,
        "pos_receipt_id": "POS98765"
    }


@tool
def fulfillment_agent(sku: str, store: str = None, mode: str = "click_and_collect"):
    """
    Fulfillment Agent.
    Reserves product for try-on or processes home delivery.
    """
    return {
        "status": "reserved" if mode == "click_and_collect" else "processing",
        "sku": sku,
        "store": store,
        "mode": mode,
        "pickup_eta_minutes": 25 if mode == "click_and_collect" else None
    }


@tool
def post_purchase_agent(order_id: str):
    """
    Post-Purchase Flow.
    Returns order confirmation message.
    """
    return f"Order {order_id} confirmed! Track it in 'My Orders'."


@tool
def normalize_sku(user_text: str):
    """
    SKU Normalizer:
    Convert free-text product names (e.g. "black air max") to valid SKUs.
    """
    text = user_text.lower()
    best = None
    best_score = 0

    for p in PRODUCT_CATALOG:
        score = 0
        if p["color"] in text:
            score += 2
        for w in text.split():
            if w in p["name"].lower():
                score += 1
        if p["category"] in text:
            score += 1

        if score > best_score:
            best_score = score
            best = p

    if not best:
        return {"status": "not_found"}

    return {
        "status": "ok",
        "sku": best["sku"],
        "name": best["name"],
        "color": best["color"],
    }


# ------------------------------------------------------------
# 8. Bind Tools + LLM
# ------------------------------------------------------------
tools = [
    product_catalog_api, normalize_sku, recommendation_agent, inventory_agent,
    loyalty_promotions_agent, payment_gateway_stub, pos_terminal_agent,
    fulfillment_agent, post_purchase_agent
]
tools_by_name = {t.name: t for t in tools}

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
sales_agent_llm = llm.bind_tools(tools)



# 9. SALES AGENT PROMPT

SALES_SYSTEM_PROMPT = """
You are an Omnichannel AI Sales Agent for a premium Indian fashion & footwear retail brand (similar to ABFRL).
You emulate a top retail stylist — warm, friendly, persuasive, knowledgeable, and highly personalized.

You operate seamlessly across:
- mobile app
- website
- WhatsApp
- in-store kiosk
- in-store POS interactions

Your goal is to deliver a unified, human-like, end-to-end shopping journey.

PRICING RULES
- ALWAYS use Indian Rupees (₹).
- NEVER use USD, $, or any foreign currency.
- Format prices as: ₹4,999 | ₹1,799 | ₹5000.
- Do NOT add taxes or shipping unless the user asks.

SKU NORMALIZATION RULE
- Users may describe products casually: "black air max", "white nike running shoes", etc.
- Whenever a user refers to such a product by description:
  1) ALWAYS call normalize_sku FIRST.
  2) Use the returned SKU for inventory_agent, fulfillment_agent, payment_gateway_stub, pos_terminal_agent.

PERSONALIZATION RULES
- Use the customer_profile actively:
  - name, age, gender, city
  - loyalty tier (GOLD / SILVER / NONE)
  - shoe size, past purchases, style_preference, budget_range
- Add human touches:
  - “Maanvi, since you prefer sportswear…”
  - “Because you purchased Nike Red Air Max earlier…”
  - “In Delhi this week, running shoes are trending because marathon season is near.”

SEASONALITY / DEMAND SPIKES
- Mention realistic demand reasons when appropriate:
  - “High demand due to Diwali festive shopping.”
  - “Pink variants sell out quickly during Valentine’s week.”
  - “Running shoes trending due to marathon season.”
  - “Black Air Max is seeing high weekend footfall.”

TOOL USAGE (WORKER AGENT ORCHESTRATION)
You have access to these Worker Agents (tools):
- product_catalog_api
- normalize_sku
- recommendation_agent
- inventory_agent
- loyalty_promotions_agent
- payment_gateway_stub
- pos_terminal_agent
- fulfillment_agent
- post_purchase_agent

Use them whenever needed.
If information is needed for accuracy → call the tool.
If the user is describing a product → normalize_sku FIRST.

SALES PSYCHOLOGY & TONE
- Ask about occasion: “Is this for daily wear, gym, or a special event?”
- Suggest cross-sell: “Would you like matching socks or a running T-shirt?”
- Add confidence: “This model is super popular this season.”
- Encourage: “You’ll love how lightweight these feel.”
Tone: friendly, warm, concise, helpful, stylish. Not robotic.

EDGE CASES
Handle gracefully:
- Payment failures → suggest UPI or split payment.
- Out-of-stock → suggest nearest stores or closest alternatives.
- User switches channel → maintain session context (if provided).
- User changes SKU → re-run SKU normalization & inventory lookup.

RESPONSE FORMAT
Always:
1. Greet naturally (“Sure Maanvi! Here are your options 👇”).
2. Show 2–4 product options with formatted prices (₹).
3. Give store-wise availability if relevant:
   “Pacific Mall (4), Motinagar (0), DLF (2), Online (12)”
4. Apply loyalty discounts if applicable, and mention them.
5. Add demand context (e.g., “Only 1 left due to weekend footfall.”)
6. Provide a clear CTA:
   “Should I reserve it for try-on at Pacific Mall or ship to your home?”
7. Never show tool call or internal system content.

IMPORTANT STOP RULE:
- If you already have all the information you need, DO NOT call a tool again.
- Only call a tool when absolutely necessary.
- If a tool has already been executed and you received its result, do NOT call the same tool again.
- If no tool is needed, reply normally in natural language and finish.

END OF SYSTEM INSTRUCTIONS
"""



# ------------------------------------------------------------
# 10. NODES (This was missing earlier)
# ------------------------------------------------------------

def sales_agent_node(state: AgentState):
    profile = state.get("customer_profile", {})
    name = profile.get("name", "there")

    system = SystemMessage(content=SALES_SYSTEM_PROMPT + f"\nCustomer name: {name}.")
    msgs = [system] + state["messages"]

    llm_response = sales_agent_llm.invoke(msgs)
    return {"messages": [llm_response]}


import json

def tool_node(state: AgentState):
    """
    Executes tools and returns their outputs in clean JSON format.
    """
    last = state["messages"][-1]

    if not isinstance(last, AIMessage) or not last.tool_calls:
        return {"messages": []}

    outputs = []
    for call in last.tool_calls:
        tool_fn = tools_by_name[call["name"]]
        args = call.get("args", {})
        result = tool_fn.invoke(args)

        outputs.append(
            ToolMessage(
                content=json.dumps(result),   # <--- FIXED
                name=call["name"],
                tool_call_id=call["id"],
            )
        )

    return {"messages": outputs}


def should_continue(state: AgentState):
    """
    Decides whether LangGraph should run a tool,
    return to the LLM, or stop the cycle.
    """
    last = state["messages"][-1]

    # If LLM requested a tool → run tool node
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tool_node"

    # If we just executed a tool → go back to the LLM
    if isinstance(last, ToolMessage):
        return "sales_agent"

    # Otherwise → stop
    return END

# ------------------------------------------------------------
# 11. Build Graph
# ------------------------------------------------------------

builder = StateGraph(AgentState)
builder.add_node("sales_agent", sales_agent_node)
builder.add_node("tool_node", tool_node)
builder.add_edge(START, "sales_agent")
builder.add_conditional_edges("sales_agent", should_continue)
builder.add_edge("tool_node", "sales_agent")

graph = builder.compile()
print("LangGraph Retail Agent compiled ✔")



