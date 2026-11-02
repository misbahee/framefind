import numpy as np
from insightface.app import FaceAnalysis


class FaceRecognitionService:
    def __init__(self):
        self.app = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
        )
        self.app.prepare(
            ctx_id=-1,
            det_size=(640, 640),
        )

    def extract_embeddings(
        self,
        image: np.ndarray,
    ) -> list[list[float]]:
        faces = self.app.get(image)

        return [
            face.normed_embedding.tolist()
            for face in faces
        ]