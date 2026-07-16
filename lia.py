import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from memory import Memory
from tools import TOOLS

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Lia:
    def __init__(self):
        self.memory = Memory()
        self.system_prompt = """
Você é Lia, uma IA parceira proativa.

Sua função é:
- Entender o objetivo do usuário.
- Pensar passo a passo.
- Escolher uma ferramenta disponível.
- Executar a ação.
- Repetir até o objetivo estar concluído.

Ferramentas disponíveis:
- SearchWeb(query): pesquisa na internet.
- CaptureImage(output_path): captura uma imagem da câmera.

Responda SEMPRE em JSON válido neste formato:
{
  "thought": "sua análise curta",
  "action": "nome da ferramenta ou NONE",
  "tool_input": "argumentos da ferramenta ou NONE"
}

Quando o objetivo estiver concluído, use:
{
  "thought": "Objetivo concluído.",
  "action": "NONE",
  "tool_input": "NONE"
}
"""

    def think(self, goal: str, history: str) -> dict:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": f"Objetivo: {goal}

Histórico:
{history}

Responda em JSON válido.",
            },
        ]

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            temperature=0.3,
        )

        text = response.choices[0].message.content.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "thought": "Falha ao interpretar a resposta do modelo.",
                "action": "NONE",
                "tool_input": "NONE",
            }

    def run(self, goal: str, max_steps: int = 10):
        self.memory.add(f"Goal: {goal}")

        for step in range(1, max_steps + 1):
            history = self.memory.get_last(12)
            decision = self.think(goal, history)

            thought = decision.get("thought", "")
            action = decision.get("action", "NONE")
            tool_input = decision.get("tool_input", "NONE")

            self.memory.add(f"Step {step} Thought: {thought}")
            self.memory.add(f"Step {step} Action: {action}")
            self.memory.add(f"Step {step} ToolInput: {tool_input}")

            if action == "NONE":
                self.memory.add("Lia: Objetivo concluído.")
                break

            tool_fn = TOOLS.get(action)

            if not tool_fn:
                result = f"Ferramenta '{action}' não encontrada."
            else:
                try:
                    if tool_input == "NONE" or tool_input == "":
                        result = tool_fn()
                    else:
                        result = tool_fn(tool_input)
                except Exception as e:
                    result = f"Erro ao executar {action}: {e}"

            self.memory.add(f"Step {step} Result: {result}")

        return self.memory.get_last(50)
