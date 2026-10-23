import re

# This example demonstrates a 4-layer architectural design for a reliable LLM-based moderation API.
# Each layer adds a specific function to enhance the trustworthiness and consistency of moderation.

def layer_1_input_preprocessing(text: str) -> str:
    """
    Layer 1: Input Preprocessing and Sanitization.
    Cleans and normalizes the input text before sending it to the LLM.
    This layer helps reduce noise and standardize input for better LLM performance.
    """
    text = text.strip()
    text = text.lower() # Normalize case for consistent matching
    text = re.sub(r'\s+', ' ', text) # Replace multiple spaces with a single space
    # Basic check for excessive special characters, which might indicate spam or obfuscation
    if len(re.findall(r'[!@#$%^&*()_+={}\[\]|\\:;"<>,.?/~`]', text)) / (len(text) + 1) > 0.3:
        print(f"  [L1] Info: High special character ratio detected.")
    print(f"  [L1] Preprocessed input: '{text}'")
    return text

def layer_2_llm_simulation(processed_text: str) -> dict:
    """
    Layer 2: LLM Interaction (Simulated).
    This layer represents the core interaction with a Large Language Model.
    In a real system, this would involve an API call to an LLM for initial content assessment.
    For this example, we simulate LLM behavior with simple keyword matching.
    """
    moderation_result = {"status": "safe", "reason": "no issues detected by LLM simulation"}

    if "hate speech" in processed_text or "kill you" in processed_text or "harm you" in processed_text:
        moderation_result = {"status": "unsafe", "reason": "explicit hate/threat detected by LLM simulation"}
    elif "spam link" in processed_text or "buy now" in processed_text or "free money" in processed_text:
        moderation_result = {"status": "flagged", "reason": "potential spam detected by LLM simulation"}
    elif "inappropriate" in processed_text or "bad word" in processed_text or "adult content" in processed_text:
        moderation_result = {"status": "flagged", "reason": "inappropriate content detected by LLM simulation"}
    
    print(f"  [L2] LLM Simulation Result: {moderation_result['status']} ({moderation_result['reason']})")
    return moderation_result

def layer_3_output_post_processing_and_verification(llm_output: dict, original_text: str) -> dict:
    """
    Layer 3: Output Post-processing and Verification.
    This critical layer enhances reliability by verifying and refining the LLM's output.
    It adds additional rules, checks, or even another LLM call to catch edge cases or override misjudgments.
    """
    final_status = llm_output["status"]
    final_reason = llm_output["reason"]

    # Example: Override LLM if a specific, highly sensitive keyword is present, regardless of LLM's initial assessment.
    forbidden_keywords = ["illegal activity", "child abuse", "bomb threat", "terrorist act"]
    for keyword in forbidden_keywords:
        if keyword in original_text.lower(): # Check original text to avoid preprocessing altering critical terms
            final_status = "unsafe"
            final_reason = f"explicit forbidden keyword '{keyword}' found (L3 override)"
            print(f"  [L3] Override: Highly sensitive keyword '{keyword}' detected. Status: {final_status}")
            break
    
    # Example: If LLM flagged, escalate for human review based on content length or complexity.
    if final_status == "flagged" and len(original_text) > 100:
        final_reason += " (long flagged content, suggesting human review for nuance)"
        print(f"  [L3] Escalation: Long flagged content, suggesting human review.")

    # Example: If LLM said 'safe' but contains suspicious URL patterns (missed by L1/L2).
    # This adds an extra layer of defense against phishing or malware links.
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    if final_status == "safe" and re.search(url_pattern, original_text.lower()):
        final_status = "flagged"
        final_reason = "suspicious URL pattern detected (L3 override)"
        print(f"  [L3] Override: Suspicious URL pattern detected. Status: {final_status}")

    print(f"  [L3] Final verified status: {final_status} ({final_reason})")
    return {"status": final_status, "reason": final_reason}

def layer_4_decision_and_action(final_moderation_result: dict) -> str:
    """
    Layer 4: Decision and Action.
    Based on the final, verified moderation status, this layer determines the appropriate platform action.
    This ensures consistent policy enforcement.
    """
    status = final_moderation_result["status"]
    reason = final_moderation_result["reason"]
    action = "unknown"

    if status == "safe":
        action = "Content Approved: Display to users."
    elif status == "flagged":
        action = f"Content Flagged: Requires human review. Reason: {reason}"
    elif status == "unsafe":
        action = f"Content Rejected: Block immediately. Reason: {reason}"
    
    print(f"  [L4] Final Action: {action}")
    return action

def moderate_content(content: str):
    """
    Orchestrates the 4-layer moderation process for a given piece of content.
    """
    print(f"\n--- Moderating: '{content}' ---")
    
    # Layer 1: Preprocessing
    processed_input = layer_1_input_preprocessing(content)
    
    # Layer 2: LLM Simulation
    llm_assessment = layer_2_llm_simulation(processed_input)
    
    # Layer 3: Post-processing and Verification
    final_assessment = layer_3_output_post_processing_and_verification(llm_assessment, content)
    
    # Layer 4: Decision and Action
    action_taken = layer_4_decision_and_action(final_assessment)
    
    return action_taken

if __name__ == "__main__":
    test_cases = [
        "Hello, this is a safe message.",
        "I hate you, you are a terrible person! This is hate speech.",
        "Check out this great deal: buy now at http://malicious.com/spam", # L3 URL check
        "This message contains inappropriate content and bad word.",
        "I will engage in illegal activity tomorrow.", # L3 override example
        "This is a long message that contains some potentially inappropriate content, but the LLM might miss it. Let's see if the post-processing layer catches it or flags it for review. It's important for reliability and consistency.", # L3 long content example
        "Just a normal chat message. No issues here.",
        "I will bomb threat the building!", # L3 override example
        "Visit my site: https://example.com/safe-link-here. It's totally safe.", # L3 URL check (flagged even if LLM says safe)
        "This is a message with !@#$%^&*() too many special characters."
    ]

    for test_case in test_cases:
        moderate_content(test_case)
