from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import *
from rest_framework.permissions import AllowAny
from django.utils.timezone import now
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import *
from django.utils.timezone import now
from rest_framework.exceptions import NotFound



# Employee Login
class EmployeeLoginAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = CustomLoginSerializer(data=request.data)
        
        if serializer.is_valid(): 
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            user = authenticate(request, username=email, password=password)
            if user is not None:
                if user.role == 1: 
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({'status' : 'True' ,'message': 'User login Successfully','token': token.key}, status=status.HTTP_200_OK)
                
                elif user.role == 0:
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({'token': token.key, 'message': 'admin login Successfully'},status.HTTP_200_OK)
                
                else:
                    return Response({'Status' : 'False','Message': 'You are not authorized to log in as an employee.'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'status' : 'False','mesaage': "Invalid email or password for Employee."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'satus' : 'False' ,"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# Employee Change Password
class PasswordChangeAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Attendance Check In And Check Out

class CheckInOutView(APIView):
    permission_classes = [AllowAny]  
    STATIC_QR_STRING = "cqt"  
    # STATIC_LOCATION = "malumichampatti" 

    def post(self, request):
        user = request.user
        data = request.data

        # Validate QR string
        qr_string = data.get('QR_string', '')
        if qr_string != self.STATIC_QR_STRING:
            return Response(
                {"status" : 'False',"error": "Invalid QR string. Please use the correct QR code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate location
        location = data.get('location', '')
        # if location != self.STATIC_LOCATION:
        #     return Response(
        #         {"error": f"Invalid location. Please be at {self.STATIC_LOCATION} to check in/out."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        # Check if the user has an active attendance record
        active_attendance = Attendance.objects.filter(user=user, check_out__isnull=True).first()

        if active_attendance:
            # Handle check-out
            active_attendance.check_out = now()
            active_attendance.QR_string = qr_string
            active_attendance.location = location
            active_attendance.save()
            return Response(
                {
                    "status" : "True",
                    "message": "Check-out successful",
                    "data": AttendanceSerializer(active_attendance).data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Handle check-in
            new_attendance = Attendance.objects.create(
                user=user,
                check_in=now(),
                QR_string=qr_string,
                location=location,
            )
            return Response(
                {
                    "status": "True",
                    "message": "Check-in successful",
                    "data": AttendanceSerializer(new_attendance).data,
                },
                status=status.HTTP_201_CREATED,
            )
    
class CheckInView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk=None):
        if pk is None:  # Handle the case for listing all attendance records
            check = Attendance.objects.raw("SELECT * FROM attendace")
            serializer = AttendanceSerializer(check, many=True)
            return Response({
                "status": "True",
                "message": "Success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        else:  # Handle the case for fetching today's check-ins for a specific user
            try:
                user = User.objects.get(pk=pk)
                today = now().date()
                today_checkins = Attendance.objects.filter(user=user, created_at__date=today)
                serializer = AttendanceSerializer(today_checkins, many=True)

                return Response({
                    "status": "True",
                    "message": "Success",
                    "data": {
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "username": user.username,
                            "user_img": user.user_img.url if user.user_img else None,
                            "reporting": user.reporting,
                            "designation": user.designation,
                            "address": user.address,
                        },
                        "today_checkin": serializer.data,
                    }
                }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({
                    "status": "False",
                    "message": "User not found"
                }, status=status.HTTP_404_NOT_FOUND)

        
from rest_framework.permissions import AllowAny

class HistoryView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            today = now().date()
            thirty_days_ago = today - timedelta(days=30)
            checkins = Attendance.objects.filter(user=user, created_at__date__gte=thirty_days_ago).order_by('-created_at')[:30]
            serializer = AttendanceSerializer(checkins, many=True)
            return Response({
                "status": "True",
                "message": "Success",
                "data": {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                    },
                    "last_30_days_checkins": serializer.data,
                }
            }, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({
                "status": "False",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
    


# Work From Home
class WorkFromHomeCheckInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id 
        data['check_in'] = now()  

        serializer = WorkFromHomeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status" : "True" ,"message": "Check-in successful.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class WorkFromHomeCheckOutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, pk):
        user = request.user
        location = request.data.get('location')

        try:
            # Find the attendance record for the user to update
            attendance = Attendance.objects.get(pk=pk, user=user, check_out__isnull=True)
            attendance.check_out = now()  
            attendance.location = location  
            attendance.save()

            serializer = WorkFromHomeSerializer(attendance)
            return Response({"status": "True","message": "Check-out successful.", "data": serializer.data}, status=status.HTTP_200_OK)
        except Attendance.DoesNotExist:
            return Response({"error": "No active check-in found for this user."}, status=status.HTTP_400_BAD_REQUEST)
        
            
            
        
from datetime import date
# post method Leave Create
class RequestLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {"error": "Authentication is required to request leave."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Include authenticated user in the request data
        data = request.data.copy()
        data['user'] = user.id  # Set the user to the authenticated user

        # Optional: Automatically set today's date for start and end dates
        if 'start_date' not in data or 'end_date' not in data:
            today = date.today()
            data['start_date'] = today
            data['end_date'] = today

        serializer = LeaveSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status":"Ture","message": "Leave request submitted successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response({"Status":"False","errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class CancelLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        today = date.today()

        try:
            leave = Leave.objects.get(pk=pk, user=user, start_date=today, end_date=today)
            leave.delete()  # Cancel the leave by deleting the record
            return Response({"status":"Ture","message": "Leave canceled successfully."}, status=status.HTTP_200_OK)
        except Leave.DoesNotExist:
            return Response({"status":"False","error": "No leave found for today to cancel."}, status=status.HTTP_400_BAD_REQUEST)


class ListLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all leaves for the authenticated user
        leaves = Leave.objects.filter(user=request.user)
        # Serialize the queryset
        serializer = LeaveSerializer(leaves, many=True)
        return Response({"status": "Ture", "message": "Leave List","data":serializer.data })
        


class UserLeaveListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        # Ensure the user ID exists and belongs to the requesting user (or admin)
        if not request.user.is_staff and request.user.id != user_id:
            return Response({"detail": "You are not authorized to view this user's leaves."}, status=403)

        # Fetch leaves for the specified user ID
        leaves = Leave.objects.filter(user_id=user_id)
        if not leaves.exists():
            raise NotFound("No leaves found for the specified user.")

        # Serialize the data
        serializer = LeaveSerializer(leaves, many=True)
        return Response({"Status":"Ture","data":serializer.data})


        
        
# get method for view profile and then put method for update your details
class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user  # Retrieve the currently authenticated user
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)  # Return updated data as response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    

# Project Create API (Admin Side)

class ProjectCreateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Project View for Employees 

class EmployeeProjectListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get projects assigned to the logged-in user
        projects = Project.objects.filter(user=request.user)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




# Project Update API (Admin Side)

class ProjectUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Project update Successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Project Delete API (Admin Side)

class ProjectDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        project.delete()
        return Response({'message': 'Project delete successfully'},status=status.HTTP_204_NO_CONTENT)




# Admin Create Holiday
class HolidayCreateAPI(APIView):
    permission_classes = [IsAuthenticated]  # Only admin can create

    def post(self, request):
        serializer = HolidaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Holiday created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin Update Holiday
class HolidayUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]  # Only admin can update

    def put(self, request, pk):
        holiday = get_object_or_404(Holiday, pk=pk)
        serializer = HolidaySerializer(holiday, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Holiday updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Admin Delete Holiday
class HolidayDeleteAPI(APIView):
    permission_classes = [IsAuthenticated]  # Only admin can delete

    def delete(self, request, pk):
        holiday = get_object_or_404(Holiday, pk=pk)
        holiday.delete()
        return Response({"message": "Holiday deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Employee List Holidays
class EmployeeHolidayListAPI(APIView):
    permission_classes = [IsAuthenticated]  # All employees can view holidays

    def get(self, request):
        holidays = Holiday.objects.all()
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# Admin Attendance List API
class AdminAttendanceListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        attendances = Attendance.objects.select_related('user').all()
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




# Admin Leave List API
class AdminLeaveListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leaves = Leave.objects.select_related('user').all()
        serializer = LeaveApprovalSerializer(leaves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



# Admin Leave Approval API
class AdminLeaveApprovalAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            leave = Leave.objects.get(pk=pk)
        except Leave.DoesNotExist:
            return Response({"detail": "Leave request not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = LeaveApprovalSerializer(leave, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



