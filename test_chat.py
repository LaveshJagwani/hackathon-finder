from chat_search import chat_search

prompt = input("Ask your hackathon query: ")

results = chat_search(prompt)

print(f"\nFound {len(results)} results:\n")

for hack in results:
    print("\nName:", hack.name)
    print("URL:", hack.url)
    print(
        "Location:",
        f"{hack.city or ''}, {hack.state or ''}, {hack.country or ''}"
    )
    print("Source:", hack.source)
    print("-" * 50)
