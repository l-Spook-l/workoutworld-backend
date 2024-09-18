from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    origins = [
        f"http://localhost:3000",
        f"http://45.137.66.74:3000",
        f"https://45.137.66.74:3000",
        f"http://vm4791907.25ssd.had.wf",
        f"https://vm4791907.25ssd.had.wf",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        # allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
        #                "Authorization"],
    )
