from openai import OpenAI


client = OpenAI(api_key="")


def generate_reply(user_text: str, system_prompt: str) -> str:
    #TODO FIX OPEN AI PROMPT
    try:


        if not system_prompt:
            return "Please, contact the account owner, I can not proceed your request now"

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # быстрый и дешевый
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"AI error: {e}")
        return "Sorry,  can not proceed your request now 🙏"