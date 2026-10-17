import streamlit as st

st.set_page_config(page_title="AI Architecture Advisor", page_icon="🧭", layout="centered")

DETERMINISTIC = "Deterministic Automation"
GENAI = "GenAI Assistant"
HITL = "HITL Agent"
BOUNDED = "Bounded Autonomous Agent"

QUESTIONS = [
    ("clear_rules", "Does the task follow clear and predictable rules?"),
    ("needs_judgment", "Does the task require language understanding, interpretation, or judgment?"),
    ("needs_action", "Does the system need to take an action in another system?"),
    ("low_risk", "Is the action low-risk and easily reversible?"),
    ("human_approval", "Should a human approve the final action before execution?"),
    ("sensitive", "Is the workflow customer-facing or financially sensitive? (optional)"),
]

# Answers for each predefined use case. Custom workflows keep whatever the user picks.
USE_CASES = {
    "Password reset": {
        "clear_rules": True, "needs_judgment": False, "needs_action": True,
        "low_risk": True, "human_approval": False, "sensitive": False,
    },
    "Meeting summary": {
        "clear_rules": False, "needs_judgment": True, "needs_action": False,
        "low_risk": True, "human_approval": False, "sensitive": False,
    },
    "Customer refund review": {
        "clear_rules": False, "needs_judgment": True, "needs_action": True,
        "low_risk": False, "human_approval": True, "sensitive": True,
    },
    "Low-value refund within policy limits": {
        "clear_rules": True, "needs_judgment": True, "needs_action": True,
        "low_risk": True, "human_approval": False, "sensitive": False,
    },
    "Contract negotiation": {
        "clear_rules": False, "needs_judgment": True, "needs_action": False,
        "low_risk": False, "human_approval": True, "sensitive": True,
    },
}

DETAILS = {
    DETERMINISTIC: {
        "why": "The rules are clear and the output is predictable, so a rules-based workflow is cheaper, faster, and easier to test than an LLM. No model is needed.",
        "flow": "User Request → Rules / Identity Check → Reset Workflow → Action",
    },
    GENAI: {
        "why": "The task needs language understanding or judgment, but it does not need to act in another system. AI can draft or summarise, and a person keeps the final decision.",
        "flow": "Input → LLM → Summary / Draft → Human",
    },
    HITL: {
        "why": "The workflow needs judgment and may trigger an action that affects a customer or the business. AI can analyse the case and recommend a step, but a human should approve it before anything runs.",
        "flow": "User → AI Agent → Policy/Data → Recommendation → Human Approval → Action",
    },
    BOUNDED: {
        "why": "The action is low-risk and reversible, and clear policy limits exist. The agent can act on its own inside those limits and escalate anything outside them.",
        "flow": "Request → Agent → Policy Check → Within Safe Limits? → Yes: Execute / No: Human Review",
    },
}


def recommend(answers):
    """Return (architecture, upgraded_to_hitl). Plain rules so each step is easy to explain and test."""
    if answers["clear_rules"] and not answers["needs_judgment"]:
        arch = DETERMINISTIC
    elif answers["needs_judgment"] and not answers["needs_action"]:
        arch = GENAI
    elif answers["needs_action"] and answers["human_approval"]:
        arch = HITL
    elif answers["needs_action"] and answers["low_risk"]:
        arch = BOUNDED
    elif answers["needs_action"]:
        # Risky action with no approval gate: default to a human-approved agent, not autonomy.
        arch = HITL
    else:
        arch = GENAI

    # Customer-facing or financially sensitive actions always get a human in the loop.
    upgraded = answers["sensitive"] and answers["needs_action"] and arch != HITL
    if upgraded:
        arch = HITL
    return arch, upgraded


def apply_use_case():
    preset = USE_CASES.get(st.session_state.use_case)
    if preset:
        for key, value in preset.items():
            st.session_state[key] = "Yes" if value else "No"


st.title("AI Architecture Advisor")
st.caption("Choose the right level of automation for a business workflow.")

with st.sidebar:
    st.header("About")
    st.write(
        "This lightweight decision-support tool helps teams choose between:\n\n"
        "- deterministic automation\n"
        "- GenAI assistance\n"
        "- HITL agents\n"
        "- bounded autonomy"
    )

st.header("1. Select or describe a use case")
st.selectbox(
    "Predefined use case",
    ["Custom workflow", *USE_CASES.keys()],
    key="use_case",
    on_change=apply_use_case,
)
st.text_area(
    "Describe your workflow (optional)",
    placeholder="e.g. Support agents review refund requests over $200 against policy.",
    key="description",
)

st.header("2. Answer the workflow questions")
for key, _ in QUESTIONS:
    st.session_state.setdefault(key, "No")

for key, label in QUESTIONS:
    st.radio(label, ["Yes", "No"], horizontal=True, key=key)

if st.button("Evaluate Workflow", type="primary"):
    answers = {key: st.session_state[key] == "Yes" for key, _ in QUESTIONS}
    arch, upgraded = recommend(answers)

    st.header("3. Recommended Architecture")
    st.success(f"**{arch}**")

    st.subheader("Why")
    st.write(DETAILS[arch]["why"])
    if upgraded:
        st.info(
            "This workflow takes an action that is customer-facing or financially sensitive, "
            "so it is upgraded to a HITL Agent for human sign-off."
        )

    st.subheader("Suggested Architecture")
    st.code(DETAILS[arch]["flow"], language="text")
