"""Quick test to bypass Gradio and test the transcription pipeline directly."""
import sys
print("Step 0: Script starting...", flush=True)

try:
    print("Step 1: Importing modules...", flush=True)
    from src.config import ApplicationConfig
    from src.download import download_url
    from src.source import get_audio_source_collection
    from src.whisper.whisperFactory import create_whisper_container
    from src.modelCache import ModelCache
    import ffmpeg
    print("Step 1 DONE: All imports successful", flush=True)

    print("Step 2: Loading config...", flush=True)
    app_config = ApplicationConfig.create_default()
    print(f"Step 2 DONE: whisper_impl={app_config.whisper_implementation}, model={app_config.default_model_name}, compute={app_config.compute_type}", flush=True)

    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        print("Usage: python test_transcribe.py <youtube_url>", flush=True)
        sys.exit(1)

    print(f"Step 3: Downloading audio from {url}...", flush=True)
    sources = get_audio_source_collection(url, None, None)
    print(f"Step 3 DONE: Got {len(sources)} source(s)", flush=True)
    for s in sources:
        print(f"  Source: {s.source_path}, duration: {s.get_audio_duration()}s", flush=True)

    print("Step 4: Creating whisper container...", flush=True)
    model_cache = ModelCache()
    model = create_whisper_container(
        whisper_implementation=app_config.whisper_implementation,
        model_name=app_config.default_model_name,
        compute_type=app_config.compute_type,
        cache=model_cache,
        models=app_config.models
    )
    print("Step 4 DONE: Container created", flush=True)

    print("Step 5: Loading model (this may take a moment)...", flush=True)
    whisper_model = model.get_model()
    print("Step 5 DONE: Model loaded", flush=True)

    print("Step 6: Creating callback and transcribing...", flush=True)
    callback = model.create_callback(language=None, task="transcribe")
    result = callback.invoke(sources[0].source_path, 0, None, None)
    print("Step 6 DONE: Transcription complete!", flush=True)

    print("\n=== RESULT ===", flush=True)
    print(f"Language: {result.get('language', 'unknown')}", flush=True)
    print(f"Text: {result['text'][:500]}", flush=True)
    print(f"Segments: {len(result.get('segments', []))}", flush=True)

except Exception as e:
    import traceback
    print(f"\n!!! ERROR at current step: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
