import hashlib
import threading
import uuid

from aws_manager import S3, Rekognition
from settings import REKOGNITION_COLLECTION, S3_BUCKET


class FaceDetector():
    def __init__(self, image_path):
        self.image_path = image_path
        self.s3 = S3(bucket_name=S3_BUCKET)
        self.rkg = Rekognition(REKOGNITION_COLLECTION, S3_BUCKET)

    @property
    def search(self):
        """
        画像に誰が写っているか
        return:
            写っている場合: ['', '']   # hogeのリスト
            写っていない場合: []
        """
        tmp_name = str(uuid.uuid4())
        self.s3.put(self.image_path, tmp_name)
        return self.rkg.search(tmp_name)
