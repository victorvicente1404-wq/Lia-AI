def search_web(query: str) -> str:
    # Implementar depois com API real
    return "Pesquisa web não implementada ainda."

def capture_image(output_path: str = "captura.png") -> str:
    return "Captura de imagem não implementada ainda."

TOOLS = {
    "SearchWeb": search_web,
    "CaptureImage": capture_image,
}
