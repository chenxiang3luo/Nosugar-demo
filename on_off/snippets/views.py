from snippets.models import Query, CustomToken,Task
from rest_framework.authentication import TokenAuthentication
from snippets.serializers import UserSerializer, QuerySerializer, CustomTokenSerializer,TaskSerializer
from django.contrib.auth.models import User
import threading
import sys
import ssl
import urllib.request
import json
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.utils import timezone
import re
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response
from snippets.util import validate_phone_number
import json


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class QueryViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    # lookup_field = 'number'

    # return filtered task with some params
    def list(self, request, *args, **kwargs):
        params = request.query_params
        user = request.user
        user_id = user.id
        number = params.get('number')
        start_date = params.get('start_date')
        end_date = params.get('end_date')

        # process date format
        if(start_date):
            start_date = start_date.replace(' ','T')
            end_date = end_date.replace(' ','T')

        # filter results with different conditions of params
        # returen all
        if(number is None and start_date is None):
            tasks = Task.objects.filter(user_id=user_id)

        # returen results of a certain number
        elif(number is not None and start_date is None):
            queries = Query.objects.filter(number__contains=number)
            queries = QuerySerializer(queries,many=True).data
            task_ids =  [query['task_id'] for query in queries]
            task_ids = list(set(task_ids))
            tasks = Task.objects.filter(id__in=task_ids,user_id=user_id)

        # return results of a certain number within a period of time
        elif(number is not None and start_date is not None):
            queries = Query.objects.filter(number__contains=number)
            queries = QuerySerializer(queries,many=True).data
            task_ids =  [query['task_id'] for query in queries]
            task_ids = list(set(task_ids))
            tasks = Task.objects.filter(id__in=task_ids,query_date__range=(start_date,end_date),user_id=user_id)

        # return results of all number within a period of time
        elif(number is None and start_date is not None):
            tasks = Task.objects.filter(query_date__range=(start_date,end_date),user_id=user_id)
        serializer = TaskSerializer(tasks, many=True)
        task_datas = serializer.data
        rep = [{'task_id':task['id'],\
            'is_batch':task['is_batch'],\
            "query_data":QuerySerializer(Query.objects.filter(task_id=task['id']), many=True).data,\
            'query_date':str(task['query_date']).replace('T',' ')
        }
        for task in task_datas]
    
        return Response(rep)

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = QuerySerializer(data=request.data)
        serializer.is_valid()
        serializer.save(user=user)
        serializer.data

        return Response({'message': 'create action executed'})
    
    # return complete information of a certain task
    def retrieve(self, request, pk):
        params = request.query_params
        user = request.user
        user_id = user.id
        number = params.get('number')
        query = Task.objects.get(id=pk)
        serializer = TaskSerializer(query)
        task = serializer.data
        if(task['user_id'] != user.id):
            return Response({'status':'请求用户错误'})
        if(number is None):
            queries = Query.objects.filter(task_id=task['id'])
        else:
            queries = Query.objects.filter(task_id=task['id'],number__contains=number)
        data = QuerySerializer(queries, many=True).data

        return Response(data)
    
    # return the process of a certain task
    @action(detail=False, methods=['get'])
    def process(self, request, pk):
        params = request.query_params
        user = request.user
        user_id = user.id
        number = params.get('number')
        query = Task.objects.get(id=pk)
        serializer = TaskSerializer(query)
        task = serializer.data
        if(task['user_id'] != user.id):
            return Response({'status':'请求用户错误'})
        return Response({'finished':task['finish_cnt'],'total':task['total_cnt']})

    # delete a certain task 
    def destroy(self, request, pk):
        user = request.user
        user_id = user.id
        queries = Task.objects.filter(id=pk,user_id=user_id).delete()
        return Response({'status': 'ok'})

    # detect the satus of phone via onther api with phone number

    # off_on_detect third-api
    @action(detail=False, methods=['post'])
    def detect_batch(self, request):
        lock = threading.Lock()
        # semaphore = threading.Semaphore(5)
        def off_on_detect(number,task_id):
            host = 'http://mobilelive.market.alicloudapi.com'
            path = '/queryonline'
            method = 'GET'
            number = number
            appcode = '52367e3b07e04f91b623203072119485'
            querys = f'number={number}'
            bodys = {}
            url = host + path + '?' + querys
            print(url)
            request = urllib.request.Request(url)
            request.add_header('Authorization', 'APPCODE ' + appcode)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            response = urllib.request.urlopen(request, context=ctx)
            content = response.read()
            mssg = json.loads(content.decode('utf-8'))
            query = {
                    "number":number,
                    'state':mssg['data']['code'],
                    'carrier': mssg['data']['extend']['isp_name']
                }
            # Maintaining data consistency
            lock.acquire()
            try:
                task_instance = Task.objects.get(id=task_id)
                task_instance.finish_cnt += 1
                task_instance.save()
                mq = QuerySerializer(data=query)
                if(mq.is_valid()):
                    mq.save(task=task_instance)
            finally:
                # release lock
                lock.release()
            # semaphore.release()
            return mq.data

        user = request.user
        token = request.auth
        key = token.key
        numbers = request.data['numbers']
        # restrick maxium number of query numbers
        numbers = numbers[:100]
        # vertify the format of numbers
        if(validate_phone_number(numbers)):
            pass
        else:
            return Response({'status':"wrong format"})

        # the case of only one number 
        if(len(numbers) > 1):
            is_batch = True
            data = {
                "is_batch":is_batch,
                "total_cnt":len(numbers)
            }
            task_s = TaskSerializer(data=data)
            
            if(task_s.is_valid()):
                task_s.save(user=user)

            threads = []
            for num in numbers:
                thread = threading.Thread(target=off_on_detect, args=(num, task_s.data['id']))
                threads.append(thread)
                thread.start()

            # count the number of queries fo a certain user 
            ct = CustomToken.objects.get(pk=key)
            ct.count += 1
            ct.save()

            rep = {
                'task_id':task_s.data['id'],
                'is_batch':is_batch,
                "len":len(numbers),
                'query_date':str(task_s.data['query_date']).replace('T',' ')
            }
            return Response(rep)
        
        # the case of a batch of numbers
        else:
            is_batch = False
            data = {
                "is_batch":is_batch,
                "total_cnt":len(numbers)
            }
            task_s = TaskSerializer(data=data)
            
            if(task_s.is_valid()):
                task_s.save(user=user)

            threads = []
            query = off_on_detect(numbers[0], task_s.data['id'])
            ct = CustomToken.objects.get(pk=key)
            ct.count += 1
            ct.save()
            rep = {
                'task_id':task_s.data['id'],
                'is_batch':is_batch,
                "query_data":[query],
                'query_date':str(task_s.data['query_date']).replace('T',' ')
            }
            return Response(rep)




# user register and login
# when logining ,return token
class UserRegistrationView(viewsets.ModelViewSet):

    # register user
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({'message': 'User registered successfully.'})

    # user login and returen token
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data['username']
        password = request.data['password']
        # vertify if user exist
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # vertify if token been send
            try:
                token = Token.objects.get(user=user)

            except Token.DoesNotExist:
                token = Token.objects.create(user=user)
                cus_token = {
                    'key': token.key,
                    'created': token.created,
                    'expires': token.created+timezone.timedelta(days=7),
                    'count': 0

                }
                serializer = CustomTokenSerializer(data=cus_token)
                if(serializer.is_valid()):
                    serializer.save(user=user)

            return Response({'status': 'ok', 'token': token.key})
        else:
            return Response({'error': 'Invalid username or password'})
