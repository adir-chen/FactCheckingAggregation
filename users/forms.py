from django import forms
from django.core.exceptions import ValidationError
from users.models import Users_Images


# def validate_image_size(image):
#     file_size = image.file.size
#     megabyte_limit = 10
#     if file_size > megabyte_limit * 1024 * 1024:
#         raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


class ImageUploadForm(forms.ModelForm):

    def clean_profile_img(self):
        megabyte_limit = 10
        image = self.cleaned_data.get('profile_img', False)
        if image:
            if image.size > megabyte_limit * 1024 * 1024:
                raise ValidationError("Image file too large (should be up to 10 MB)")
            return image
        else:
            raise ValidationError("Couldn't read uploaded image")

    class Meta:
        model = Users_Images
        fields = ('profile_img',)
        labels = {
            "profile_img": "Select an image"
        }


