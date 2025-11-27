from google.genai import types
try:
    if hasattr(types.Part, 'from_text'):
        print("types.Part.from_text exists")
    else:
        print("types.Part.from_text DOES NOT EXIST")
        
    # Try constructor
    try:
        p = types.Part(text="hello")
        print("types.Part(text='...') works")
    except Exception as e:
        print(f"types.Part(text='...') failed: {e}")

except Exception as e:
    print(f"Error: {e}")
