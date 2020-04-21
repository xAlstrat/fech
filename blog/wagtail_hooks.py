from wagtail.admin.site_summary import SummaryItem
from wagtail.admin.utils import get_site_for_user
from wagtail.core import hooks

from blog.models import Event, New, Benefit, CCEE, ONG, Transparency, Archive


@hooks.register('construct_main_menu')
def hide_snippets_menu_item(request, menu_items):
  menu_items[:] = [item for item in menu_items if item.name != 'explorer']


class SnippetSummaryItem(SummaryItem):
  order = 100

  def get_context(self):
    count = self.model.objects.count()
    site_name = get_site_for_user(self.request.user)['site_name']

    return {
      'total_docs': count,
      'site_name': site_name,
    }

  def is_shown(self):
      return True


class EventSnippetSummaryItem(SnippetSummaryItem):
  model = Event
  template = 'home/site_summary_events.html'


class NewSnippetSummaryItem(SnippetSummaryItem):
  model = New
  template = 'home/site_summary_news.html'


class BenefitSnippetSummaryItem(SnippetSummaryItem):
  model = Benefit
  template = 'home/site_summary_benefits.html'


class CCEESnippetSummaryItem(SnippetSummaryItem):
  model = CCEE
  template = 'home/site_summary_ccees.html'

class ONGSnippetSummaryItem(SnippetSummaryItem):
  model = ONG
  template = 'home/site_summary_ongs.html'

class TransparencySnippetSummaryItem(SnippetSummaryItem):
  model = Transparency
  template = 'home/site_summary_transparency.html'

class ArchiveSnippetSummaryItem(SnippetSummaryItem):
  model = Archive
  template = 'home/site_summary_archive.html'

@hooks.register('construct_homepage_summary_items')
def update_pages_summary(request, menu_items):
  menu_items[:] = [EventSnippetSummaryItem(request), NewSnippetSummaryItem(request), BenefitSnippetSummaryItem(request),
                   ONGSnippetSummaryItem(request),
                   TransparencySnippetSummaryItem(request),
                   ArchiveSnippetSummaryItem(request),
                   CCEESnippetSummaryItem(request)]



@hooks.register('describe_collection_contents')
def append_snippets_summary(collection):
  return None