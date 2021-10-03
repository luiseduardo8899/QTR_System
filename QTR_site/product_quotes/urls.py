from django.conf.urls import url
from . import views

app_name = 'product_quotes'
urlpatterns = [
    # ex: /languagebits/
    url(r'^generate_quote/$', views.generate_quote, name='generate_quote'),
    #url(r'^generate_license/$', views.generate_license, name='generate_license'),
    #url(r'^kana/(?P<kana_id>[0-9]+)/$', views.kana_detail, name='kana_detail'),
    #url(r'^grammar/(?P<grammar_id>[0-9]+)/$', views.grammar_detail, name='grammar_detail'),
    #url(r'^kanji/jlpt/(?P<jlpt_level>[0-9]+)/$', views.kanji_list, name='kanji_list'),
    #url(r'^kanji/(?P<kanji_id>[0-9]+)/$', views.kanji_detail, name='kanji_detail'),
    #url(r'^grammar/(?P<grammar_id>[0-9]+)/$', views.grammar_detail, name='grammar_detail'),
    #url(r'^vocab/(?P<vocab_id>[0-9]+)/$', views.vocab_detail, name='vocab_detail'),
    #url(r'^vocab/stats/(?P<vocab_id>[0-9]+)/$', views.vocab_stats_detail, name='vocab_stats_detail'),
    #url(r'^vocab/check_def_answer/(?P<vocab_id>[0-9]+)/$', views.check_def_answer, name='check_def_answer'),
    #url(r'^vocab/check_fur_answer/(?P<vocab_id>[0-9]+)/$', views.check_fur_answer, name='check_fur_answer'),
    ]
