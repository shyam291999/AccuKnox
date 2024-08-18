from rest_framework import serializers

from user.models import User, Friendship


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    repassword = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', "phone", "password", "repassword", "first_name", "last_name"]
    
    def validate(self, data):
        phone = data.get('phone')
       
        if len(phone) != 10:
            raise serializers.ValidationError({'message': "Phone Number must be of 10 length"})
        
        if not data['phone'].isdigit():
            raise serializers.ValidationError({"message": "Phone Number must contain digits only"})
        
        return data

    def create(self, validated_data):
        repassword = validated_data.pop('repassword')
        password = validated_data.get('password')

        if password != repassword:
            raise serializers.ValidationError({'message': 'Passwords and RePassword do not match.'})
        
        user = User(**validated_data)
        user.set_password(password)  # Hash the password
        user.save()
        return user
    

    


class FriendshipSerializer(serializers.ModelSerializer):

    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = '__all__'
