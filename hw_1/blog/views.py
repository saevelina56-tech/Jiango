from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Article, Book, Category
from django.db.models import Count, Q


NEWS = [
    {'id': 1, 'title': 'News 1', 'content': 'Content of news 1'},
    {'id': 2, 'title': 'News 2', 'content': 'Content of news 2'},
    {'id': 3, 'title': 'News 3', 'content': 'Content of news 3'},
]

# Create your views here.
def home(request):
    articles = Article.objects.filter(is_published=True)
    context = {'articles': articles}
    return render(request, 'home.html', context)

def books(request):
    books_list = Book.objects.all()
    return JsonResponse({'books': list(books_list.values())})

def article_detail(request, id):
    article = next((i for i in NEWS if i['id'] == id), None)
    print(article)
    context = {'article': article}
    return render(request, 'article_detail.html', context)

def article_list(request):
    articles = Article.objects.filter(is_published=True).select_related('author', 'category')
    return render(request, 'article_list.html', {'articles': articles})

def article_by_category(request, category_name):
    category = get_object_or_404(Category, slug=category_name)
    articles = Article.objects.filter(
        is_published = True,
        category = category,
    ).select_related('author', 'category')
    
    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, 'article_list.html', context)

def article_search(request):
    query = request.GET.get('q', '').strip()
    articles = []
    search_message = ''
    
    context = {
        'articles': articles,
        'query': query,
        'search_message': search_message,
    }
    return render(request, 'article_search.html', context)
    

def article_stats(request):
    total_articles = Article.objects.filter(is_published=True).count()
    
    category_stats = Article.objects.filter(
        is_published=True
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    categories = Category.objects.filter(
        articles__is_published=True
    ).distinct().values_list('name', flat=True)
    
    stats = {
        'total_articles': total_articles,
        'articles_by_category': list(category_stats),
        'all_categories': list(categories),
    }
    
    return JsonResponse(stats, json_dumps_params={'ensure_ascii': False, 'indent': 2})

@csrf_exempt
def create_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        new_id = len(NEWS) + 1
        NEWS.append({'id': new_id, 'title': title, 'content': content})
        return JsonResponse({'status': 'success', 'message': f'Article "{title}" created successfully!'})
    return render(request, 'create_article.html')