from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from user_profile.models import *
from .models import *
from .forms import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def home(request):
    blogs = Blog.objects.order_by('-date')
    tags = Tag.objects.order_by('-date')

    context = {
        'blogs':blogs,
        'tags':tags
    }
    return render(request,'index.html',context)


def blogs(request):
    queryset = Blog.objects.order_by('-date')
    tags = Tag.objects.order_by('-date')
    page = request.GET.get('page',1)
    paginator = Paginator(queryset,4)
    
    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')

    context = {
        'blogs':blogs,
        'tags':tags,
        'paginator':paginator
    }
    return render(request,'blog.html',context)

def blog_details(request,slug):
    form = TextForm()
    blogs = Blog.objects.get(slug=slug)
    tags = Tag.objects.order_by('-date')
    category = Category.objects.get(id=blogs.category.id)
    related_blogs = category.category_blogs.all()
    liked_by = request.user in blogs.likes.all()
    if request.method == "POST" and request.user.is_authenticated:
        form = TextForm(request.POST)
        if form.is_valid():
            Comment.objects.create(
                user = request.user,
                blog = blogs,
                text = form.cleaned_data.get('text')
            )
            return redirect('blog_details', slug=slug)
    context = {
        'blogs':blogs,
        'tags':tags,
        'related_blogs':related_blogs,
        'form':form,
        'liked_by':liked_by
    }
    return render(request,'blog_details.html',context)

def category_blogs(request,slug):
    category = Category.objects.get(slug=slug)
    queryset = category.category_blogs.all()
    tags = Tag.objects.order_by('-date')[:5]
    all_blogs = Blog.objects.order_by('-date')[:5]
    page = request.GET.get('page',1)
    paginator = Paginator(queryset,2)
    
    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')

    context = {
        'blogs':blogs,
        'tags':tags,
        'paginator':paginator,
        'all_blogs':all_blogs
    }
    return render(request, 'category_blogs.html',context)

def tag_blogs(request,slug):
    tags = Tag.objects.get(slug=slug)
    queryset = tags.tag_blogs.all()
    tags = Tag.objects.order_by('-date')[:5]
    all_blogs = Blog.objects.order_by('-date')[:5]
    page = request.GET.get('page',1)
    paginator = Paginator(queryset,2)
    
    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')

    context = {
        'blogs':blogs,
        'tags':tags,
        'paginator':paginator,
        'all_blogs':all_blogs
    }
    return render(request, 'tag_blogs.html',context)

@login_required(login_url='login')
def add_reply(request, blog_id, comment_id):
    form = TextForm()
    blogs = Blog.objects.get(id=blog_id)
    if request.method == "POST":
        form = TextForm(request.POST)
        if form.is_valid():
            get_comment = Comment.objects.get(id=comment_id)
            Reply.objects.create(
                user = request.user,
                comment = get_comment,
                text = form.cleaned_data.get('text')
            )
    return redirect('blog_details',slug=blogs.slug)

@login_required(login_url='login')
def like_blog(request,pk):
    blogs = Blog.objects.get(pk=pk)
    context = {}
    if request.user in blogs.likes.all():
        blogs.likes.remove(request.user)
        context['liked']= False
        context['like_count']= blogs.likes.all().count()

    else:
        blogs.likes.add(request.user)
        context['liked']= True
        context['like_count']= blogs.likes.all().count()

    return JsonResponse(context, safe=False)

def search_blog(request):
    search_key = request.GET.get('search',None)
    recent_blogs = Blog.objects.order_by('-date')
    tags = Tag.objects.order_by('-date')
    if search_key:
        blogs = Blog.objects.filter(
            Q(title__icontains=search_key) |
            Q(category__title__icontains=search_key) |
            Q(user__username__icontains=search_key) |
            Q(tags__title__icontains=search_key)
        ).distinct()
        context={
            'blogs':blogs,
            'search_key':search_key,
            'recent_blogs':recent_blogs,
            'tags':tags
            }
        return render(request,'search.html',context)
    else:
        blogs = Blog.objects.order_by('-date')
        context = {
            'blogs':blogs
            }
        return redirect('home')
 
@login_required(login_url='login')
def my_blogs(request):
    queryset = request.user.user_blogs.all()
    page = request.GET.get('page',1)
    paginator = Paginator(queryset,6)
    delete = request.GET.get('delete',None)
    
    if delete:
        blog = Blog.objects.get(pk=delete)
        if request.user.pk != blog.user.pk:
            return redirect('home')
        blog.delete()
        messages.success(request,"Blog has deleted succesfully")
        return redirect('my_blogs')
    
    try:
        blogs = paginator.page(page)
    except EmptyPage:
        blogs = paginator.page(1)
    except PageNotAnInteger:
        blogs = paginator.page(1)
        return redirect('blogs')

    context = {
        'blogs':blogs,
        'paginator':paginator,
    }
    
    return render(request,'myblogs.html',context)


@login_required(login_url='login')
def add_blogs(request):
    form = AddBlogForm()
    if request.method == "POST":
        form = AddBlogForm(request.POST, request.FILES)
        if form.is_valid():
            tags = request.POST['tags'].split(',')
            user = User.objects.get(pk=request.user.pk)
            category = Category.objects.get(pk=request.POST['category'])
            blog = form.save(commit=False)
            blog.user = user
            blog.category = category
            blog.save()
            
            for tag in tags:
                tag_input = Tag.objects.filter(
                    title__iexact = tag.strip(),
                    slug = slugify(tag.strip())
                )
                if tag_input.exists():
                    t = tag_input.first()
                    blog.tags.add(t)
                    
                else:
                    if tag != '':
                        new_tag = Tag.objects.create(
                            title = tag.strip(),
                            slug = slugify(tag.strip())
                        )
                        blog.tags.add(new_tag)
            messages.success(request, "Blog added succesfully")
            return redirect('blog_details', slug = blog.slug)
        else:
            print(form.errors)
    context = {
        'form':form
    }
    return render(request,'addblogs.html',context)

@login_required(login_url='login')
def update_blogs(request, slug):
    blogs = Blog.objects.get(slug=slug)
    form = AddBlogForm(instance=blogs)
    
    if request.method == "POST":
        form = AddBlogForm(request.POST, request.FILES, instance=blogs)
        if form.is_valid():
            if request.user.pk != blogs.user.pk:
                return redirect('home')
            
            tags = request.POST['tags'].split(',')
            user = User.objects.get(pk=request.user.pk)
            category = Category.objects.get(pk=request.POST['category'])
            blog = form.save(commit=False)
            blog.user = user
            blog.category = category
            blog.save()
            
            for tag in tags:
                tag_input = Tag.objects.filter(
                    title__iexact = tag.strip(),
                    slug = slugify(tag.strip())
                )
                if tag_input.exists():
                    t = tag_input.first()
                    blog.tags.add(t)
                    
                else:
                    if tag != '':
                        new_tag = Tag.objects.create(
                            title = tag.strip(),
                            slug = slugify(tag.strip())
                        )
                        blog.tags.add(new_tag)
            messages.success(request, "Blog updated succesfully")
            return redirect('blog_details', slug = blog.slug)
        else:
            print(form.errors)
    context = {
        'form':form,
        'blogs':blogs
    }
    return render(request,'update-blog.html',context)







