import os
from openai import OpenAI
from tools import TOOLS
from memory import Memory

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Lia:
    def __init__(self):
        self.memory = Memory()
        self.system_prompt = (
            "Você é Lia, uma IA parceira proativa. "
            "Você recebe um objetivo e deve:
"
            "1. Pensar passo a passo.
"
            "2. Escolher uma ferramenta disponível.
"
            "3. Executar a ação.
"
            "4. Repetir até o objetivo estar completo.

"
            "Ferramentas disponíveis:
"
            "- SearchWeb(query): pesquisa na internet.
"
            "- CaptureImage(output_path): captura uma imagem da câmera.

"
            "Responda sempre no formato:
"
            "Thought: ...
"
            "Action: <nome da ferramenta>
"
            "ToolInput: <argumentos da ferramenta>
"
            "Quando o objetivo estiver completo, responda:
"
            "Thought: Objetivo concluído.
"
            "Action: NONE
"
            "ToolInput: NONE"
        )

    def think(self, goal: str, history: str) -> dict:
        prompt = (
            f"{self.system_prompt}

"
            f"Objective: {goal}
"
            f"History:
{history}

"
            "Now respond with Thought, Action, and ToolInput."
        )

        resp = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        text = resp.messages[-1].content.strip()

        thought = ""
        action = ""
        tool_input = ""

        for line in text.split("
"):
            if line.startswith("Thought:"):
                thought = line.split("Thought:", 1)[1].strip()
            elif line.startswith("Action:"):
                action = line.split("Action:", 1)[1].strip()
            elif line.startswith("ToolInput:"):
                tool_input = line.split("ToolInput:", 1)[1].strip()

        return {"thought": thought, "action": action, "tool_input": tool_input}

    def run(self, goal: str, max_steps: int = 20):
        self.memory.add(f"Goal: {goal}")
        step = 0

        while step < max_steps:
            step += 1
            history = self.memory.get_last(10)
            decision = self.think(goal, history)

            self.memory.add(f"Step {step}: Thought: {decision['thought']}")
            self.memory.add(f"Step {step}: Action: {decision['action']}")

            if decision["action"] == "NONE":
                self.memory.add("Lia: Objetivo concluído.")
                break

            tool_name = decision["action"]
            tool_input_str = decision["tool_input"]
            parts = [p.strip() for p in tool_input_str.split(",")]

            result = f"Tool {tool_name} não implementada ainda."

            self.memory.add(f"Step {step}: Result: {result}")

        return self.memory.get_last(50)
