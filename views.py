from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Topic, Entry
from .forms import TopicForm, EntryForm

# Create your views here.

def index(request):
	"""Домашняя страница приложения Learning Log."""
	return render(request, 'learning_logs/index.html')

def more_inf(request):
	return render(request,'learning_logs/more_inf.html')

class TopicsHome(ListView):
	model = Topic
	template_name = 'learning_logs/topics.html'
	context_object_name = 'topics'
	
	def get_queryset(self):
		public_topics = Topic.objects.filter(public=True).order_by('date_added')
		if self.request.user.is_authenticated:
			private_topics = Topic.objects.filter(owner=self.request.user).order_by('date_added')
			topics = public_topics | private_topics
		else:
			topics = public_topics
		return topics


class ShowTopic(LoginRequiredMixin, DetailView):
	model = Topic
	template_name = 'learning_logs/topic.html'
	context_object_name = 'topic'
	slug_url_kwarg = 'topic_slug'
  
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		topic = get_object_or_404(Topic, slug=self.kwargs['topic_slug'])
		check_topic_owner(topic.owner, self.request)
		context['entries'] = topic.entry_set.order_by('-date_added')
		return context


class AddTopic(LoginRequiredMixin, CreateView):  
	form_class = TopicForm
	template_name = 'learning_logs/new_topic.html'  

	def form_valid(self, form):
		new_topic = form.save(commit=False)
		new_topic.owner = self.request.user
		new_topic.save()
		return redirect('learning_logs:topics')
	
class AddEntry(LoginRequiredMixin, CreateView):
	form_class = EntryForm
	template_name = 'learning_logs/new_entry.html'
	slug_url_kwarg = 'topic_slug'

	def form_valid(self, form):
		topic = get_object_or_404(Topic, slug=self.kwargs['topic_slug'])
		check_topic_owner(topic.owner, self.request)
		new_entry = form.save(commit=False)
		new_entry.topic = topic
		new_entry.save()
		return redirect('learning_logs:topic', topic_slug=topic.slug)


class EditEntry(LoginRequiredMixin, UpdateView):
	model = Entry
	form_class = EntryForm
	template_name = 'learning_logs/edit_entry.html'
	context_object_name = 'topic'
	slug_url_kwarg = 'entry_slug'

	def form_valid(self, form):
		entry = get_object_or_404(Entry, slug=self.kwargs['entry_slug'])
		topic = entry.topic
		check_topic_owner(topic.owner, self.request)
		form.save()
		return redirect('learning_logs:topic', topic_slug=topic.slug)


def check_topic_owner(owner, request):
	if owner != request.user:
		raise Http404
