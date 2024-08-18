from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from user.serializers import UserSerializer, FriendshipSerializer
from user.models import User, Friendship
from django.db.models import Q
from rest_framework.authentication import BasicAuthentication
from django.utils import timezone
from datetime import timedelta


class SignupView(CreateAPIView, ListAPIView):

    serializer_class = UserSerializer
    permission_classes = [AllowAny]



class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        # breakpoint()
        email = request.data.get('email')
        username = request.data.get('username')
        phone = request.data.get('phone')

        password = request.data.get('password')

        if not email and not username and phone:
            return Response({'error': 'Email or Mobile Number or username is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if  not password:
            return Response({'error': 'password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine if identifier is email, username, or mobile number
        user = None
        
        if email:  # Assuming '@' indicates an email
            user = User.objects.filter(email=email).first()
        elif phone:  # Assuming all digits indicates a mobile number
            user = User.objects.filter(mobile_number=phone).first()
        else:
            user = User.objects.filter(username=username).first()
        
        if user and user.check_password(password):
            return Response({'message': 'Login successful'})
        
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    
class UserSearchView(ListAPIView):

    serializer_class = UserSerializer
    PageNumberPagination = PageNumberPagination
    # authentication_classes = [BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        
        searchParam = self.request.query_params.get('q', '')
        # will match exactly with email and will match normally with username
        return User.objects.filter(Q(email__iexact=searchParam) | Q(username__icontains=searchParam)) 
    

class sendFriendRequest(APIView):

    def post(self, request, user_id,  *args, **kwargs):
        
        from_user = request.user
        try:
            to_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try: 
            #checking friend request is already been send or not
            if Friendship.objects.filter(from_user=from_user, to_user=to_user, status='pending').exists():
                return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

            one_minute_ago = timezone.now() - timedelta(minutes=1)
            recent_requests = Friendship.objects.filter(from_user=from_user, created_at__gte=one_minute_ago).count()

            # dont allow if the request is greate then 4 in a min
            if recent_requests >= 4:
                return Response({'error': 'Friend request limit reached'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

            Friendship.objects.create(from_user=from_user, to_user=to_user, status="pending")

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
        return Response({'message': 'Friend request sent'})



class AcceptUserRequest(APIView):

    def post(self, request, friendship_id, action):
        
        try:
            friendship_obj = Friendship.objects.get(id=friendship_id, to_user=request.user, status='pending')

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            if action == 'accept':
                friendship_obj.status = 'accepted'
            elif action == 'reject':
                friendship_obj.status = 'rejected'
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

            friendship_obj.save()
            return Response({'message': f'Friend request {action}ed'})

        except Exception as e:
            return Response({"error": f"{e}"})



# FriendListView  PendingFriendRequestsView

class FriendListView(ListAPIView):

    serializer_class = UserSerializer

    def get_queryset(self):
        # return objs having request.user                
        return self.request.user.friends.filter(request_received__status='accepted')

        # return User.objects.filter(request_send=self.request.user, status='accepted')
        # user = User.objects.filter(user=self.request.user.id)
        # return self.request.user.request_send.all().filter(status='accepted')



class PendingFriendRequestsView(ListAPIView):
    serializer_class = FriendshipSerializer

    def get_queryset(self):
        #show the pending reqeust both who have send to whome
        return self.request.user.request_received.filter(status='pending')
