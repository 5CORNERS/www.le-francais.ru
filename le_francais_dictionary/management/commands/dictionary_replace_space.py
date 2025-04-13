from urllib.parse import urlparse

import pysftp
from django.core.management import BaseCommand
from le_francais_dictionary.models import Word, WordTranslation, UnifiedWord
from le_francais_dictionary.tts import FTP_FR_WORDS_PATH, FTP_RU_WORDS_PATH
import os


class Command(BaseCommand):
    help = (
        "Find all voiceover files with spaces in their filenames, replace spaces "
        "with underscores, and update the corresponding _polly_url fields in Word, "
        "WordTranslation, UnifiedWord, and unified translation URLs."
    )

    def handle(self, *args, **options):
        # Iterate through Word objects to update files
        self.stdout.write("Processing `Word` objects...")
        for word in Word.objects.all():
            if word._polly_url and ' ' in word._polly_url:
                new_url = self.process_url(word._polly_url, FTP_FR_WORDS_PATH)
                if new_url:
                    word._polly_url = new_url
                    word.save(update_fields=["_polly_url"])
                    self.stdout.write(
                        f"Updated Word (cd_id={word.cd_id}): {word._polly_url}"
                    )

        # Iterate through WordTranslation objects to update files
        self.stdout.write("Processing `WordTranslation` objects...")
        for translation in WordTranslation.objects.all():
            if translation._polly_url and ' ' in translation._polly_url:
                new_url = self.process_url(translation._polly_url, FTP_RU_WORDS_PATH)
                if new_url:
                    translation._polly_url = new_url
                    translation.save(update_fields=["_polly_url"])
                    self.stdout.write(
                        f"Updated WordTranslation (id={translation.id}): {translation._polly_url}"
                    )

        # Iterate through UnifiedWord objects to update files
        self.stdout.write("Processing `UnifiedWord` objects...")
        for unified_word in UnifiedWord.objects.all():
            # Update unified word URL
            if unified_word.word_polly_url and ' ' in unified_word.word_polly_url:
                new_word_url = self.process_url(unified_word.word_polly_url, FTP_FR_WORDS_PATH)
                if new_word_url:
                    unified_word.word_polly_url = new_word_url

            # Update unified translation URL
            if unified_word.translation_polly_url and ' ' in unified_word.translation_polly_url:
                new_translation_url = self.process_url(
                    unified_word.translation_polly_url,
                    FTP_RU_WORDS_PATH
                )
                if new_translation_url:
                    unified_word.translation_polly_url = new_translation_url

            unified_word.save(
                update_fields=["word_polly_url", "translation_polly_url"]
            )
            self.stdout.write(
                f"Updated UnifiedWord (id={unified_word.id}): "
                f"Word Polly URL: {unified_word.word_polly_url}, "
                f"Translation Polly URL: {unified_word.translation_polly_url}"
            )

        self.stdout.write("Processing complete!")

    def process_url(self, url, path):
        """
        Helper method to process the URL, replace spaces with underscores,
        and rename the underlying file on an FTP server.

        Args:
            url (str): The HTTP URL of the file.

        Returns:
            str: The updated URL with spaces replaced by underscores, or
                None if the operation fails.
        """
        try:
            # Parse the URL to extract information
            file_name = url.rsplit("/", 1)[1]
            new_file_name = file_name.replace(' ', '_')

            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None
            srv = pysftp.Connection(
                host=os.environ.get('SFTP_FILES_LE_FRANCAIS_HOSTNAME'),
                username=os.environ.get('SFTP_FILES_LE_FRANCAIS_USERNAME'),
                password=os.environ.get('SFTP_FILES_LE_FRANCAIS_PASSWORD'),
                cnopts=cnopts
            )

            with srv.cd(path):
                srv.rename(file_name, new_file_name)

            # Construct the new URL and return it
            new_url = url.rsplit("/", 1)[0] + "/" + new_file_name
            return new_url

        except Exception as e:
            self.stderr.write(f"Error processing URL {url}: {e}")
            return None
