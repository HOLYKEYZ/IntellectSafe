
try:
    from transformers import pipeline
    print("Transformers available.")
    classifier = pipeline("status", model="bert-base-uncased") # Just checking import, model download might fail if offline
    print("Pipeline loaded.")
except Exception as e:
    print(f"Error: {e}")
