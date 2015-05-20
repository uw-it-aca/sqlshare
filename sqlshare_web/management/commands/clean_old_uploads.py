from django.conf import settings
from django.core.management.base import BaseCommand
from optparse import make_option
import time
import os


class Command(BaseCommand):
    help = "This cleans uploaded files that have been abandoned."

    option_list = BaseCommand.option_list + (
        make_option('--dry-run',
                    dest='dry_run',
                    action="store_true",
                    help=("Don't actually delete the files, but show what "
                          "would be removed."),
                    ),
        make_option('--verbose',
                    dest='verbose',
                    action="store_true",
                    help=("Print information about what's happening."),
                    ),

        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        verbose = options["verbose"]
        now = time.time()

        base_dir = settings.SQLSHARE_FILE_CHUNK_PATH
        HOURS_48 = 60 * 60 * 48
        max_age = getattr(settings, "SQLSHARE_FILE_MAX_AGE", HOURS_48)
        for root, dirs, files in os.walk(base_dir, topdown=False):
            for file in files:
                path = os.path.join(root, file)
                age = now - os.stat(path).st_mtime

                if age > max_age:
                    if verbose:
                        print("Delete file: %s" % path)
                    if not dry_run:
                        os.remove(path)

            for dir in dirs:
                path = os.path.join(root, dir)
                age = now - os.stat(path).st_mtime

                if age > max_age:
                    if verbose:
                        print("Delete directory: %s" % path)
                    if not dry_run:
                        try:
                            os.rmdir(path)
                        except OSError as ex:
                            # This can be things like a person's top level
                            # directory including other files that are too new
                            # to be purged.
                            pass
