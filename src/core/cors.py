from fastapi.middleware.cors import CORSMiddleware

from src.core.config import ALLOWED_ORIGINS


def setup_cors(app):
    origins = ALLOWED_ORIGINS.split(",")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        # allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
        #                "Authorization"],
    )
