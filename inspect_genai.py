from google.genai import types
try:
    print("types.Part attributes:", dir(types.Part))
    if hasattr(types.Part, 'from_data'):
        print("types.Part.from_data exists")
    else:
        print("types.Part.from_data DOES NOT EXIST")
except Exception as e:
    print(f"Error inspecting types.Part: {e}")
