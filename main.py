import uvicorn


def run() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Failed to start server: {exc}")
