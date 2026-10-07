from app.core.config import get_settings

def generate_answer(question: str, facts: list[str]) -> str:
    settings = get_settings()
    context = "\n".join(f"- {x}" for x in facts)
    if not settings.use_bedrock:
        return f"Based on the available claim and policy information:\n{context}"

    from langchain_aws import ChatBedrockConverse
    model = ChatBedrockConverse(model=settings.bedrock_model_id, region_name=settings.aws_region, temperature=0)
    prompt = f"""You are a healthcare support assistant. Use only the supplied facts. Do not invent coverage decisions. If evidence is insufficient, say so.\n\nQuestion: {question}\n\nFacts:\n{context}\n\nGive a concise member-friendly answer."""
    return model.invoke(prompt).content
