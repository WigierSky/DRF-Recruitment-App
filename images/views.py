import datetime
import os
from PIL import Image as PilImage
from io import BytesIO
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.authentication import BasicAuthentication
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse, Http404
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_migrate


from .serializers import (
    ImageSerializer,
    UserProfileSerializer,
    FeatureSerializer,
    PlanSerializer,
)
from .models import Image, UserProfile, Feature, Plan


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class FeatureViewSet(viewsets.ModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

# Method to make first default Plans and Features for them
@receiver(post_migrate)
def create_initial_plans_and_features(sender, **kwargs):
    if sender.name == "images":
        if not Feature.objects.exists():
            Feature.objects.create(name="Original image")
            Feature.objects.create(name="Thumbnail 200px", pixels=200)
            Feature.objects.create(name="Thumbnail 400px", pixels=400)
            Feature.objects.create(name="Expiring link")

        if not Plan.objects.exists():
            feature1 = Feature.objects.get(name="Original image")
            feature2 = Feature.objects.get(name="Thumbnail 200px")
            feature3 = Feature.objects.get(name="Thumbnail 400px")
            feature4 = Feature.objects.get(name="Expiring link")
            basic = Plan.objects.create(name="Basic")
            basic.features.add(feature2)
            premium = Plan.objects.create(name="Premium")
            premium.features.add(feature1, feature2, feature3)
            enterprise = Plan.objects.create(name="Enterprise")
            enterprise.features.add(feature1, feature2, feature3, feature4)


@api_view(["POST", "GET"])
@authentication_classes([BasicAuthentication])
def upload_image(request):
    user = request.user.profile
    plan = user.plan
  
    if "image" not in request.data:
        return Response({"error": "No image in data."}, status=status.HTTP_400_BAD_REQUEST)

    uploaded_image = request.data["image"]

    pil_image = PilImage.open(uploaded_image)
    pil_image = pil_image.convert("RGB")

    image_instance = Image(user=user)
    original_image_io = BytesIO()
    pil_image.save(original_image_io, format="JPEG")
    original_image_file = SimpleUploadedFile("original_image.jpg", original_image_io.getvalue())
    image_instance.image.save("original_image.jpg", original_image_file)

    links = {}

    for feature in plan.features.all():
        # first feature for original image
        if feature.name == "Original image":
            links["original_image"] = request.build_absolute_uri(image_instance.image.url)  # Oryginalne zdjęcie
        elif feature.name == "Expiring link":
        #second feature for expiring links
            if "expire_time" in request.data:
                expire_time = request.data["expire_time"]
                expiring_time = datetime.datetime.now() + datetime.timedelta(seconds=int(expire_time))

                links["expiring_link"] = request.build_absolute_uri(image_instance.image.url + "/expires_in=" + str(expiring_time)) 
        else:
        # third feature for thumbnail with customizable size
            pix = feature.pixels
            thumbnail_io = BytesIO()
            thumbnail = pil_image.copy()
            thumbnail.thumbnail((pix, pix))
            thumbnail.save(thumbnail_io, format="JPEG")
            thumbnail_file = SimpleUploadedFile("thumbnail_" + str(pix) + "px.jpg", thumbnail_io.getvalue())
            image_instance.thumbnail.save("thumbnail_" + str(pix) + "px.jpg", thumbnail_file)
            links["thumbnail_" + str(pix) + "px"] = request.build_absolute_uri(image_instance.thumbnail.url)

    # Add user nick and plan name to response
    response_data = {
        "links": links,
        "user_nick": request.user.username,
        "user_plan": plan.name,
    }

    return Response(response_data, status=status.HTTP_201_CREATED)


def thumbnail_view(request, thumbnail_name):
    # Path to thumbnails
    thumbnails_dir = os.path.join(settings.MEDIA_ROOT, "thumbnails")
    thumbnail_path = os.path.join(thumbnails_dir, thumbnail_name)

    try:
        with open(thumbnail_path, "rb") as thumbnail_file:
            response = HttpResponse(thumbnail_file.read(), content_type="image/jpeg")
        return response
    except FileNotFoundError:
        raise Http404


def image_view(request, image_name):
    image_dir = os.path.join(settings.MEDIA_ROOT, "images")
    image_path = os.path.join(image_dir, image_name)

    try:
        with open(image_path, "rb") as image_file:
            response = HttpResponse(image_file.read(), content_type="image/jpeg")
        return response
    except FileNotFoundError:
        raise Http404

@api_view(["GET", "POST"])
def expire_link(request, image_name, expires_in_str):

    image_dir = os.path.join(settings.MEDIA_ROOT, 'images')
    image_path = os.path.join(image_dir, image_name)

    expires_in = datetime.datetime.strptime(expires_in_str, "%Y-%m-%d %H:%M:%S.%f")

    if expires_in > datetime.datetime.now():
        try:
            # Otwórz miniaturę i odczytaj jej zawartość jako plik binarny
            with open(image_path, 'rb') as image_file:
                response = HttpResponse(image_file.read(), content_type='image/jpeg')
            return response
        except FileNotFoundError:
            raise Http404
    else:
        return HttpResponse("Link expired", status=404)