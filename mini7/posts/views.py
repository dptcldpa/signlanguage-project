from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
import json 
from django.utils import timezone

from django.contrib.auth.models import User
from django.core import serializers

from .models import Post
from .forms import PostForm

# Create your views here.
# CRUD
# - Create
# - Read
# - Update
# - Delete


def posts_id_none(request):
    if request.method == 'GET':
        return read_posts_list(request)
    
    elif request.method == 'POST':
        return create_post(request)



def posts_id_not_none(request, post_id):
    """ 
    게시글 CRUD
    """
    if request.method == 'GET':
        # 포스트 조회
        return read_post(request, post_id)            

    elif request.method == 'DELETE':
        # 포스트 삭제
        return delete_post(request, post_id)

    elif request.method == 'PUT':
        # 포스트 업데이트
        return update_post(request, post_id)


def read_posts_list(request):
    """
    게시판 조회
    """
    # 입력 인자
    page = request.GET.get('page', 1)
    
    # 조회
    p_list = Post.objects.order_by('-create_date')

    #페이징 처리
    paginator = Paginator(p_list, 10)
    page_obj = paginator.get_page(page)

    serialized_page = serializers.serialize('python', page_obj)
    for data in serialized_page:
        fields = data['fields']

        fields['postId'] = data['pk']
        fields['createdAt'] = fields.pop('create_date')
        user_id = fields['user_id']
        username = User.objects.get(id=user_id).username
        fields['username'] = username
    
    data = {"data":[data['fields'] for data in serialized_page]}

    return JsonResponse(data, safe=False)


def create_post(request):
    """
    포스트 생성
    """
    body = json.loads(request.body)
    
    post = Post()
    post.title = body['title']
    post.content = body['content']
    post.create_date = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    post.views = 0
    post.user_id = User.objects.get(username='admin') # request.session.get('user_id')

    try:
        post.save()
        return JsonResponse({"message":"success"}, status=200)
    except:
        return JsonResponse({"message": "fail"}, status=400)
    

def read_post(request, post_id):
    """
    포스트 조회
    """

    post = get_object_or_404(Post, pk=post_id)

    # 접속할 때마다 조회수 1 증가
    post.views += 1
    post.save()

    data = {
        "postId": post_id,
        "title": post.title,
        "content": post.content,
        "createdAt": post.create_date,
        "views": post.views,
        "userId": post.user_id.id,
        "username": post.user_id.username
    }
    return JsonResponse(data, status=200)


def update_post(request, post_id):
    """
    포스트 수정
    """
    post = get_object_or_404(Post, id=post_id)
    body = json.loads(request.body)
    
    # 데이터 업데이트
    post.title = body['title']
    post.content = body['content']
    
    # 포스트 저장
    post.save()

    try:
        post.save()
        return JsonResponse({"message":"success"}, status=200)
    except:
        return JsonResponse({"message": "fail"}, status=400)
    
    

def delete_post(request, post_id):
    """
    포스트 삭제
    """
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return JsonResponse({"message": "success: 포스트가 삭제되었습니다."}, status=200)
    except Post.DoesNotExist:
        return JsonResponse({"message": "fail: 해당 포스트가 존재하지 않습니다."}, status=404)