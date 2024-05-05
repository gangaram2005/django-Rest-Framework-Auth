from rest_framework import serializers
from account.models import User
from xml.dom import ValidationErr
from django.forms import ValidationError
# reset password ko lagi email ma link send garna ko laig
from django.utils.encoding import smart_str, force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from account.utils import Util
#from .utils import send_email

class UserRegistrationSerializer(serializers.ModelSerializer):
    # we are writing this we need to confirm password field in our registration request
    password2=serializers.CharField(style={'inpute_type':'password'},write_only=True)
    class Meta:
        model=User
        fields=['email','name','password','password2', 'tc']
        extra_kwargs={
            'password':{'write_only':True}
        }
    # validating passwaord and confirm password while registration
    def validate(self,attrs):
        password=attrs.get('password')
        password2=attrs.get('password2')
        if password !=password2:
            raise serializers.ValidationError('Password and Confirm password are does not matched')
        return attrs
    
    def create(self,validate_data):
        return User.objects.create_user(**validate_data)  #Custom User banayera yo lekhnu pareko ho
        

# User Login Serializer
class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=255)
    class Meta:
        model=User
        fields=['email','password']
        
# User Profile serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['email','password']
        
        
# User Password Chage 
class UserChangePasswordSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    class Meta:
        fields=['password','password2']
    # validating passwaord and confirm password while User Wants to change password
    def validate(self,attrs):
        password=attrs.get('password') 
        password2=attrs.get('password2') 
        user=self.context.get('user') # yo chai views bata liyera aako 
        if password !=password2:
            raise serializers.ValidationError('Password and Confirm password are does not matched')
        user.set_password(password)
        user.save()
        return attrs
    
class SendResetPasswordEmailSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    fields = ['email']

  def validate(self, attrs):
    email = attrs.get('email')
    if User.objects.filter(email=email).exists():
      user = User.objects.get(email = email)
      uid = urlsafe_base64_encode(force_bytes(user.id))
      print('Encoded UID', uid)
      token = PasswordResetTokenGenerator().make_token(user)
      print('Password Reset Token', token)
      link = 'http://localhost:3000/api/user/reset/'+uid+'/'+token
      print('Password Reset Link', link)
      # Send EMail
      body = 'Click Following Link to Reset Your Password '+link
      data = {
        'subject':'Reset Your Password',
        'body':body,
        'to_email':user.email
      }
      # Util.send_email(data)
      return attrs
    else:
      raise serializers.ValidationError('You are not a Registered User')
            
        
class UserPasswordResetSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=255,style={'input_type':'password'},write_only=True)
    class Meta:
        fields=['password','password2']
    # validating passwaord and confirm password while User Wants to change password
    def validate(self,attrs):
        try:
            password=attrs.get('password') 
            password2=attrs.get('password2') 
            uid=self.context.get('uid') # yo chai views bata liyera aako 
            token=self.context.get('token') # yo chai views bata liyera aako 
            
            if password !=password2:
                raise serializers.ValidationError('Password and Confirm password are does not matched')
            id=smart_str(urlsafe_base64_decode(uid))
            user=User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise ValidationErr('Token is not valid or expired')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user,token)
            raise ValidationErr('Token is not valid or expired')