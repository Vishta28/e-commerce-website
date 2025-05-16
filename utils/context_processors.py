from django_user_agents.utils import get_user_agent
from django.shortcuts import render

def header_render(request):
	user_agent = get_user_agent(request)
	return {'user_agent': user_agent}