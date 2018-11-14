from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import DefaultStorage

from candidates.csv_helpers import list_to_csv, memberships_dicts_for_csv
from elections.models import Election


def safely_write(output_filename, memberships_list):
    """
    Use Django's storage backend to write the CSV file to the MEDIA_ROOT.

    If using S3 (via Django Storages) the file is atomically written when the
    file is closed (when the context manager closes).

    That is, the file can be opened and written to but nothing changes at
    the public S3 URL until the object is closed. Meaning it's not possible to
    have a half written file.

    If not using S3, there will be a short time where the file is empty
    during write.
    """

    csv = list_to_csv(memberships_list)
    file_store = DefaultStorage()
    with file_store.open(output_filename, "wb") as out_file:
        out_file.write(csv.encode("utf-8"))


class Command(BaseCommand):

    help = "Output CSV files for all elections"

    def add_arguments(self, parser):
        parser.add_argument(
            "--site-base-url",
            help="The base URL of the site (for full image URLs)",
        )
        parser.add_argument(
            "--election",
            metavar="ELECTION-SLUG",
            help="Only output CSV for the election with this slug",
        )

    def slug_to_file_name(self, slug):
        return "{}-{}.csv".format(self.output_prefix, slug)

    def handle(self, **options):
        if options["election"]:
            try:
                election = Election.objects.get(slug=options["election"])
                election_slug = election.slug
            except Election.DoesNotExist:
                message = "Couldn't find an election with slug {election_slug}"
                raise CommandError(
                    message.format(election_slug=options["election"])
                )
        else:
            election_slug = None

        self.options = options
        self.output_prefix = "candidates"

        membership_by_election, elected_by_election = memberships_dicts_for_csv(
            election_slug
        )

        # Go through the membership_by_election dict and write each one as a CSV
        for slug, memberships in membership_by_election.items():
            safely_write(self.slug_to_file_name(slug), memberships)

        # If we're not outputting a single election, output all elections
        if not election_slug:
            sorted_elections = sorted(
                membership_by_election.keys(),
                key=lambda key: key.split(".")[-1],
            )
            all_memberships = []
            all_elected = []
            for slug in sorted_elections:
                all_memberships += membership_by_election[slug]
                all_elected += elected_by_election[slug]
            safely_write(self.slug_to_file_name("all"), all_memberships)
            safely_write(self.slug_to_file_name("elected-all"), all_elected)
