from src.agent import get_llm

def main():
    llm = get_llm()
    response = llm.invoke("Email: Hi team, the prototype deadline is Sept 25. Ali → frontend, Ruman → backend. Summarize in 2 lines and list tasks.")

    # Show raw response and actual text
    print("RAW RESPONSE:", response)
    if hasattr(response, "content"):
        print("MODEL OUTPUT:", response.content)

if __name__ == "__main__":
    main()
