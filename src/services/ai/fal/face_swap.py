import cv2
import insightface
from insightface.app import FaceAnalysis
from insightface.model_zoo import model_zoo

swapper = model_zoo.get_model('inswapper_128.onnx', download=True)

face_app = FaceAnalysis('image-generator-bot')
face_app.prepare(ctx_id=0)


class FaceSwapper:
    def save_face_data(self, user_photo: str):
        # 1. embed лица пользователя
        user_face = face_app.get(user_photo)[0]
        embedding = user_face.embedding
        return embedding

    def swap_face(self, image: str, face_data: str):
        # 2. применяем SimSwap
        source = cv2.imread("source.jpg")  # лицо пользователя
        target = cv2.imread("target.jpg")  # сгенерированное фото

        # 3. Находим лицо
        source_face = face_app.get(source)[0]
        target_face = face_app.get(target)[0]

        result = swapper.get(target, target_face, source_face)