import os

import boto3

from settings import AWS_PROFILE_NAME


class S3(object):
    def __init__(self, bucket_name):
        session = boto3.Session(profile_name=AWS_PROFILE_NAME)
        self.client = session.client('s3')
        self.bucket = bucket_name

    def put(self, local_path, s3_path):
        with open(local_path, 'rb') as data:
            self.client.upload_fileobj(data, self.bucket, s3_path)

    def get_file_list(self, dir_name):
        response = self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=dir_name,
        )
        if 'Contents' in response:
            return [e['Key'] for e in response['Contents']]
        else:
            return []


class Rekognition(object):

    def __init__(self, collection_name, s3_bucket):
        session = boto3.Session(profile_name=AWS_PROFILE_NAME)
        self.client = session.client('rekognition')
        self.collection = collection_name
        self.s3_bucket = s3_bucket
        self.s3 = S3(bucket_name='av-face')

        self._create_collection()

    def _create_collection(self):
        resp = self.client.list_collections()
        already_created = False
        while True:
            # ページネーションしてすでにcollectionが作られているか確認
            if self.collection in resp['CollectionIds']:
                already_created = True
                break
            elif 'NextToken' in resp:
                continue
            else:
                break

        if not already_created:
            self.client.create_collection(CollectionId=self.collection)

    def index_face(self, image_name, hashed_av_name):
        response = self.client.index_faces(
            CollectionId=self.collection,
            Image={
                'S3Object': {
                    'Bucket': self.s3_bucket,
                    'Name': image_name,
                }
            },
            ExternalImageId=hashed_av_name,
            DetectionAttributes=['ALL']
        )

        if response['FaceRecords'] == []:
            print('Face is not Detected')
            return False

        if len(response['FaceRecords']) > 1:
            print('has too many Faces')
            return False

        face_id = response['FaceRecords'][0]['Face']['FaceId']
        gender = response['FaceRecords'][0]['FaceDetail']['Gender']['Value']
        if gender == 'Female':
            print('Face is Indexed')
            return True
        else:
            self.delete_face(face_id)
            print('Face is Male')
            return False

    def delete_face(self, face_id):
        response = self.client.delete_faces(
            CollectionId=self.collection,
            FaceIds=[face_id]
        )

    def search(self, image_name, threshold=70, limit=5):
        response = self.client.search_faces_by_image(
            CollectionId=self.collection,
            Image={
                'S3Object': {
                    'Bucket': self.s3_bucket,
                    'Name': image_name,
                }
            },
            MaxFaces=10,
            FaceMatchThreshold=threshold
        )
        similarities = {f['Face']['ExternalImageId']: f['Similarity'] for f in response['FaceMatches']}
        counter = 0
        result = []
        for person_id, sim in sorted(similarities.items(), key=lambda dict: dict[1], reverse=True):
            result.append((person_id, sim))
            counter += 1
            if counter >= limit:
                break
        return result



"""
index_face の返り値
{
    'ResponseMetadata': {
        'RequestId': 'f7a02f17-1ce8-11e7-8cf8-19a229d9d06e',
        'HTTPStatusCode': 200,
        'HTTPHeaders': {'x-amzn-requestid': 'f7a02f17-1ce8-11e7-8cf8-19a229d9d06e', 'date': 'Sun, 09 Apr 2017 05:54:19 GMT', 'connection': 'keep-alive', 'content-type': 'application/x-amz-json-1.1', 'content-length': '3070'},
        'RetryAttempts': 0},
    'OrientationCorrection': 'ROTATE_0',
    'FaceRecords': [
        {
            'Face': {
                'Confidence': 99.91897583007812,
                'ImageId': '2fcc2cc3-0cee-59db-b0c7-51036deb24ef',
                'FaceId': '2ff7711e-8028-5153-ab39-8e38b5a8a65d',
                'BoundingBox': {'Top': 0.22333332896232605, 'Width': 0.5153220891952515, 'Height': 0.3444444537162781, 'Left': 0.09672711789608002},
                'ExternalImageId': 'hinata'},
            'FaceDetail': {
                'MouthOpen': {'Confidence': 99.98037719726562, 'Value': False},
                'EyesOpen': {'Confidence': 99.99968719482422, 'Value': True},
                'Landmarks': [
                    {'Y': 0.41974854469299316, 'Type': 'eyeLeft', 'X': 0.2515293061733246},
                    {'Y': 0.3341997265815735, 'Type': 'eyeRight', 'X': 0.3726670742034912},
                    {'Y': 0.43759068846702576, 'Type': 'nose', 'X': 0.3748127520084381},
                    {'Y': 0.48354652523994446, 'Type': 'mouthLeft', 'X': 0.39773914217948914},
                    {'Y': 0.4299016296863556, 'Type': 'mouthRight', 'X': 0.4911462962627411},
                    {'Y': 0.41329067945480347, 'Type': 'leftPupil', 'X': 0.2595714330673218},
                    {'Y': 0.3292524814605713, 'Type': 'rightPupil', 'X': 0.3810458481311798},
                    {'Y': 0.4224875569343567, 'Type': 'leftEyeBrowLeft', 'X': 0.17392446100711823},
                    {'Y': 0.3963016867637634, 'Type': 'leftEyeBrowRight', 'X': 0.194625586271286},
                    {'Y': 0.3800581693649292, 'Type': 'leftEyeBrowUp', 'X': 0.23668716847896576},
                    {'Y': 0.3333851993083954, 'Type': 'rightEyeBrowLeft', 'X': 0.29822221398353577},
                    {'Y': 0.29856082797050476, 'Type': 'rightEyeBrowRight', 'X': 0.3308200538158417},
                    {'Y': 0.2805359661579132, 'Type': 'rightEyeBrowUp', 'X': 0.3835222125053406},
                    {'Y': 0.43153148889541626, 'Type': 'leftEyeLeft', 'X': 0.22830510139465332},
                    {'Y': 0.40804630517959595, 'Type': 'leftEyeRight', 'X': 0.2790931761264801},
                    {'Y': 0.41330647468566895, 'Type': 'leftEyeUp', 'X': 0.24268780648708344},
                    {'Y': 0.4261501729488373, 'Type': 'leftEyeDown', 'X': 0.2582009732723236},
                    {'Y': 0.3542858362197876, 'Type': 'rightEyeLeft', 'X': 0.3537868559360504},
                    {'Y': 0.3158814311027527, 'Type': 'rightEyeRight', 'X': 0.3953779935836792},
                    {'Y': 0.32932236790657043, 'Type': 'rightEyeUp', 'X': 0.36073529720306396},
                    {'Y': 0.33819323778152466, 'Type': 'rightEyeDown', 'X': 0.38268351554870605},
                    {'Y': 0.4558020532131195, 'Type': 'noseLeft', 'X': 0.3793877959251404},
                    {'Y': 0.42932265996932983, 'Type': 'noseRight', 'X': 0.4228433072566986},
                    {'Y': 0.4610694944858551, 'Type': 'mouthUp', 'X': 0.4341852366924286},
                    {'Y': 0.47661322355270386, 'Type': 'mouthDown', 'X': 0.46342507004737854}],
                'AgeRange': {'High': 38, 'Low': 20},
                'Eyeglasses': {'Confidence': 99.94702911376953, 'Value': False},
                'Emotions': [
                    {'Confidence': 22.481822967529297, 'Type': 'HAPPY'},
                    {'Confidence': 10.103500366210938, 'Type': 'CONFUSED'},
                    {'Confidence': 1.5643119812011719, 'Type': 'CALM'}],
                'Confidence': 99.91897583007812,
                'Sunglasses': {'Confidence': 99.93952178955078, 'Value': False},
                'Mustache': {'Confidence': 97.114501953125, 'Value': False},
                'Gender': {'Confidence': 100.0, 'Value': 'Female'},
                'Smile': {'Confidence': 88.62902069091797, 'Value': True},
                'Quality': {'Sharpness': 99.99880981445312, 'Brightness': 42.08735275268555},
                'Beard': {'Confidence': 99.03729248046875, 'Value': False},
                'Pose': {'Roll': -46.50354766845703, 'Yaw': -12.461899757385254, 'Pitch': -9.539398193359375},
                'BoundingBox': {'Top': 0.22333332896232605, 'Width': 0.5153220891952515, 'Height': 0.3444444537162781, 'Left': 0.09672711789608002}
            }
        }
    ]
}
"""

"""
searchの返り値
{
    'ResponseMetadata': {
        'RequestId': '3fea08b4-1ce5-11e7-9bf1-1571af8ddfc4',
        'RetryAttempts': 0,
        'HTTPStatusCode': 200,
        'HTTPHeaders': {
            'content-type': 'application/x-amz-json-1.1',
            'date': 'Sun, 09 Apr 2017 05:27:41 GMT',
            'x-amzn-requestid': '3fea08b4-1ce5-11e7-9bf1-1571af8ddfc4',
            'connection': 'keep-alive',
            'content-length': '836'
        }
    },
    'SearchedFaceBoundingBox': {
        'Top': 0.23111110925674438,
        'Width': 0.23000000417232513,
        'Height': 0.30666667222976685,
        'Left': 0.6855555772781372
    },
    'FaceMatches': [
        {
            'Similarity': 85.9066162109375,
            'Face': {
                'FaceId': '2d6bd5e1-9de7-5549-93db-2cfc5f238f2a',
                'ExternalImageId': 'hinata',
                'ImageId': '2fcc2cc3-0cee-59db-b0c7-51036deb24ef',
                'BoundingBox': {'Top': 0.22333300113677979, 'Width': 0.5153220295906067, 'Height': 0.34444400668144226, 'Left': 0.09672710299491882},
                'Confidence': 99.91899871826172}
        }, {
            'Similarity': 81.46985626220703,
            'Face': {
                'FaceId': '1dd1f2c5-b0d8-5213-903d-dba75a345d91',
                'ExternalImageId': 'hinata',
                'ImageId': 'c7a9897e-ac9a-5b01-b0d3-e4e3791e0c15',
                'BoundingBox': {'Top': 0.06555560231208801, 'Width': 0.28684601187705994, 'Height': 0.1911109983921051, 'Left': 0.4969770014286041},
                'Confidence': 99.89920043945312}}
    ],
    'SearchedFaceConfidence': 99.63330078125}
"""
