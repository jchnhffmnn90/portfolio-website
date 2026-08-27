from django.core.management.base import BaseCommand, CommandError

from projects.services.sync import sync_projects_from_github


class Command(BaseCommand):
    help = "Sync GitHub repositories into the Project database model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="GitHub username to sync (defaults to GITHUB_USERNAME in settings).",
        )
        parser.add_argument(
            "--include-forks",
            action="store_true",
            help="Include forked repositories.",
        )

    def handle(self, *args, **options):
        username = options.get("username")
        include_forks = options.get("include_forks", False)

        self.stdout.write("Starting GitHub project synchronization...")

        try:
            result = sync_projects_from_github(
                username=username,
                include_forks=include_forks,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully synced projects: {result.created} created, "
                    f"{result.updated} updated (total {result.total} repos processed)."
                )
            )
        except ValueError as err:
            raise CommandError(str(err)) from err
        except Exception as err:
            raise CommandError(f"Failed to sync projects: {err}") from err
