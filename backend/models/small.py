from .base import ModelProvider

class SmallModelProvider(ModelProvider):
    name = "Small LLM"
    tier = "SMALL"

    def simulate_response(self, query: str) -> str:
        q = query.lower()
        # Factual Benchmark handlers
        if 'trench' in q:
            return "The Mariana Trench is the deepest oceanic trench in the world, with Challenger Deep reaching nearly 11,000 meters."
        elif 'apollo 11' in q or 'humans on the moon' in q:
            return "Apollo 11 landed the first humans on the Moon in 1969."
        elif 'new zealand' in q and 'capital' in q:
            return "The capital city of New Zealand is Wellington."
        elif 'penicillin' in q:
            return "Alexander Fleming discovered penicillin in 1928."
        elif 'atomic number 1' in q:
            return "Hydrogen is the chemical element with atomic number 1."
        elif 'confirmed moons' in q:
            return "Saturn has the most confirmed moons in our solar system, with over 140 known satellites."
        elif 'the hobbit' in q:
            return "J.R.R. Tolkien wrote the fantasy novel 'The Hobbit'."
        elif 'connective tissue' in q or 'structural protein' in q:
            return "Collagen is the primary structural protein found in skin and other connective tissues."
        elif 'dhcp' in q:
            return "DHCP stands for Dynamic Host Configuration Protocol."
        elif '2016 summer olympic' in q or 'olympic games' in q and '2016' in q:
            return "Brazil hosted the 2016 Summer Olympic Games in Rio de Janeiro."
        # General Factual Queries
        elif 'capital' in q and 'japan' in q:
            return "The capital of Japan is Tokyo."
        elif 'capital' in q and 'france' in q:
            return "The capital of France is Paris."
        elif 'capital' in q:
            return "The capital is Paris."
        elif 'telephone' in q:
            return "Alexander Graham Bell is widely credited with patenting the first practical telephone in 1876."
        elif 'supervised' in q:
            return "Supervised learning is a machine learning paradigm where models are trained using labeled input-output pairs."
        elif 'write' in q or 'code' in q or 'function' in q:
            return "def reverse_string(s: str) -> str:\n    return s[::-1]"
        elif 'summarize' in q or 'summary' in q:
            return "In summary, the key finding is that concise communication reduces unnecessary overhead."
        else:
            return "This is a direct, concise answer from the Small model."
