# news/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.cache import cache
from django.db.models import Count
from .models import News, Category
from .forms import NewsForm
from django.db import models

class NewsListView(ListView):
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 5

    def get_queryset(self):
        news = cache.get('news_list')
        if not news:
            news = News.objects.filter(is_published=True).select_related('author', 'category')
            cache.set('news_list', news, 300)  
        return news

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        categories = cache.get('categories_with_counts')
        if not categories:
            categories = Category.objects.annotate(
                news_count=Count('news', filter=models.Q(news__is_published=True))
            )
            cache.set('categories_with_counts', categories, 600)  
        
        context['categories'] = categories
        return context

class NewsDetailView(DetailView):
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news_item'

    def get_object(self):
        obj = super().get_object()
        obj.views += 1
        obj.save(update_fields=['views'])
        return obj

    def get(self, request, *args, **kwargs):
        user_id = request.user.id if request.user.is_authenticated else 0
        cache_key = f'news_detail_{self.kwargs["pk"]}_user_{user_id}'
        
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response
        
        response = super().get(request, *args, **kwargs)
        cache.set(cache_key, response, 300)
        return response

class NewsCreateView(LoginRequiredMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news:list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        cache.delete('news_list')
        cache.delete('categories_with_counts')
        return response

class NewsUpdateView(LoginRequiredMixin, UpdateView):
    model = News
    form_class = NewsForm
    template_name = 'news/news_form.html'
    success_url = reverse_lazy('news:list')

    def get_queryset(self):
        return News.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_editing'] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        cache.delete('news_list')
        cache.delete('categories_with_counts')
        cache.delete(f'news_detail_{self.object.id}_user_*')
        return response

class NewsDeleteView(LoginRequiredMixin, DeleteView):
    model = News
    template_name = 'news/news_confirm_delete.html'
    success_url = reverse_lazy('news:list')

    def get_queryset(self):
        return News.objects.filter(author=self.request.user)

    def delete(self, request, *args, **kwargs):
        news_id = self.get_object().id
        response = super().delete(request, *args, **kwargs)
        cache.delete('news_list')
        cache.delete('categories_with_counts')
        cache.delete(f'news_detail_{news_id}_user_*')
        return response