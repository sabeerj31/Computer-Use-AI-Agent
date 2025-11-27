from google.genai import types
import base64

try:
    # Try the inline_data with Blob approach
    blob = types.Blob(data=b"test", mime_type="text/plain")
    part = types.Part(inline_data=blob)
    print("SUCCESS: types.Part(inline_data=blob) worked")
except Exception as e:
    print(f"FAILED: types.Part(inline_data=blob) failed: {e}")

try:
    # Try the inline_data with dict approach
    part = types.Part(inline_data={"data": b"test", "mime_type": "text/plain"})
    print("SUCCESS: types.Part(inline_data=dict) worked")
except Exception as e:
    print(f"FAILED: types.Part(inline_data=dict) failed: {e}")
