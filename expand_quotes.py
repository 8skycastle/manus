import os
import re
from openai import OpenAI

client = OpenAI()

def expand_quote(quote_text):
    prompt = f"""
다음은 짧은 명언입니다. 이 명언의 의미를 깊게 살리면서, 분량을 2배 정도로 늘려주세요.
사용자가 요청한 스타일은 다음과 같습니다:
예시: "인생은 초콜릿 상자 같아. 뭘 받을지 모르지." -> "인생은 초콜릿 상자와 같아요.\\n무엇을 집을지 알 수 없지만,\\n그래서 살아볼 만한 거예요."

규칙:
1. 원문의 핵심 메시지를 유지하되, 감성적이고 따뜻한 문체로 다듬어주세요.
2. 2~3문장 정도로 구성해 주세요.
3. 줄바꿈(\\n)을 적절히 섞어서 가독성을 높여주세요. (문자열 내에서 \\n으로 표현)
4. 결과물에 따옴표를 포함하지 마세요.

원문: {quote_text}
확장된 문장:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        # 불필요한 따옴표 제거
        content = content.strip('"').strip("'")
        return content
    except Exception as e:
        print(f"Error expanding quote: {e}")
        return quote_text

def process_file():
    file_path = "/home/ubuntu/habit_quotes_website/client/src/data/quotes-1000.ts"
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 정규식으로 { text: "...", ... } 형태 추출
    # 여러 줄에 걸쳐 있을 수 있으므로 re.DOTALL 사용
    pattern = re.compile(r'\{ text: "(.*?)", source: "(.*?)", category: "(.*?)", type: "(.*?)" \}', re.DOTALL)
    
    def replacement(match):
        text, source, category, qtype = match.groups()
        print(f"Expanding: {text[:20]}...")
        expanded = expand_quote(text)
        # JS 문자열 내에서 안전하게 이스케이프
        expanded = expanded.replace('"', '\\"').replace('\n', '\\n')
        return f'{{ text: "{expanded}", source: "{source}", category: "{category}", type: "{qtype}" }}'

    # 1000개를 한꺼번에 처리하면 시간이 많이 걸리므로, 우선 구조를 파악하기 위해 
    # re.sub를 사용하여 순차적으로 변환
    new_content = pattern.sub(replacement, content)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully updated quotes-1000.ts")

if __name__ == "__main__":
    process_file()
