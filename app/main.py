from app.router import AgentRouter


def main():
    router = AgentRouter()

    print("=== FLYHOUSE AI AGENT ===")
    print("Escribe tu pregunta.")
    print("Escribe 'salir' para terminar.\n")

    while True:
        user_input = input("Tú: ").strip()

        if user_input.lower() in ["salir", "exit", "quit"]:
            print("Sistema finalizado.")
            break

        if not user_input:
            print("Escribe una pregunta válida.\n")
            continue

        try:
            area, response = router.route(user_input)
            print(f"\nÁrea detectada: {area}")
            print(f"Respuesta:\n{response}\n")
        except Exception as e:
            print(f"\nError al procesar la consulta: {e}\n")


if __name__ == "__main__":
    main()