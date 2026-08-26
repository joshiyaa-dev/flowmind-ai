from huggingface_hub import snapshot_download

MODEL_ID = "microsoft/Phi-3-mini-4k-instruct"


if __name__ == "__main__":
    path = snapshot_download(repo_id=MODEL_ID)
    print(f"Downloaded {MODEL_ID} to: {path}")
