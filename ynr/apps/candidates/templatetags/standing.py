from slugify import slugify

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Prefetch
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from popolo.models import Membership

from uk_results.models import CandidateResult

register = template.Library()


def get_candidacy(person, election):
    try:
        if "uk_results" in settings.INSTALLED_APPS:
            memberships_qs = person.memberships.prefetch_related(
                Prefetch(
                    "result",
                    CandidateResult.objects.select_related("result_set"),
                )
            )
        else:
            memberships_qs = person.memberships.all()
        return memberships_qs.get(
            role=election.candidate_membership_role,
            post_election__election=election,
        )
    except Membership.DoesNotExist:
        return None


def get_known_candidacy_prefix_and_suffix(candidacy):
    prefix = ""
    suffix = ""
    candidate_result = getattr(candidacy, "result", None)
    if candidate_result:
        # Then we're OK to display this result:
        suffix += "<br>"
        if candidate_result.is_winner:
            suffix += '<span class="candidate-result-confirmed candidate-result-confirmed-elected">Elected!</span>'
        else:
            suffix += '<span class="candidate-result-confirmed candidate-result-confirmed-not-elected">Not elected</span>'
        suffix += ' <span class="vote-count">({} votes)</span>'.format(
            candidate_result.num_ballots
        )
        suffix += "<br>"

    return prefix, suffix


@register.filter
def post_in_election(person, election):
    # FIXME: this is inefficient, but similar to the previous
    # implementation.
    candidacy = get_candidacy(person, election)
    if candidacy:
        link = '<a href="{cons_url}">{cons_name}</a>'.format(
            cons_url=reverse(
                "constituency",
                kwargs={
                    "election": election.slug,
                    "post_id": candidacy.post.slug,
                    "ignored_slug": slugify(candidacy.post.short_label),
                },
            ),
            cons_name=candidacy.post.short_label,
        )
        result = '<span class="constituency-value-standing-link">{}'.format(
            link
        )
        if candidacy.post_election.cancelled:
            result += ' <abbr title="The poll for this election was cancelled">❌</abbr>'
        result += "</span>"
        result += ' <span class="party">{}</span>'.format(candidacy.party.name)
        prefix, suffix = get_known_candidacy_prefix_and_suffix(candidacy)
        result = prefix + result + suffix
    else:
        if election in person.not_standing.all():
            if election.current:
                result = (
                    '<span class="constituency-value-not-standing">%s</span>'
                    % _("Not standing")
                )
            else:
                result = (
                    '<span class="constituency-value-not-standing">%s</span>'
                    % _("Did not stand")
                )
        else:
            if election.current:
                result = (
                    '<span class="constituency-value-unknown">%s</span>'
                    % _("No information yet")
                )
            else:
                result = (
                    '<span class="constituency-not-standing">%s</span>'
                    % _("Did not stand")
                )
    return mark_safe(result)


@register.filter
def election_decision_known(person, election):
    return person.get_elected(election) is not None


@register.filter
def was_elected(person, election):
    return bool(person.get_elected(election))
