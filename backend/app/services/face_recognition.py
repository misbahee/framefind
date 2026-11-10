import numpy as np
from insightface.app import FaceAnalysis


class FaceRecognitionService:
    def __init__(self):
        self._app = None

    def _load(self):
        """Load the model on first use — only runs in the Celery worker process."""
        if self._app is None:
            self._app = FaceAnalysis(
                name="buffalo_l",
                providers=["CPUExecutionProvider"],
            )
            self._app.prepare(
                ctx_id=-1,
                det_size=(640, 640),
            )

    def extract_embeddings(
        self,
        image: np.ndarray,
    ) -> list[list[float]]:
        self._load()

        faces = self._app.get(image)

        return [
            face.normed_embedding.tolist()
            for face in faces
        ]


face_recognition_service = FaceRecognitionService()