from flask_restx import Namespace, Resource
from flask import request

from app.services.service_image import ImageService

ns_image = Namespace('images', description='Image API')


@ns_image.route("")
class ImagesResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_service = ImageService()

    def post(self):
        if 'file' not in request.files:
            return {'error': 'Missing file'}, 400

        entity = request.form['entity']
        entity_id = request.form['entity_id']
        category = request.form['category']
        file = request.files['file']

        s3_key = self.image_service.upload_image(entity, entity_id, file, category)
        img_url = self.image_service.get_presigned_url(s3_key)

        return {
            "img_url": img_url
        }, 200


@ns_image.route("/<path:s3_key>")
class ImageResource(Resource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_service = ImageService()

    def delete(self, s3_key):
        result = self.image_service.delete_image(s3_key=s3_key)
        if result:
            return {"message": "success"}, 200
        else:
            return {"error": "File not found"}, 404
